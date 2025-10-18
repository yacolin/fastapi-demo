from typing import Optional

from fastapi import APIRouter, Depends, status
from pydantic import BaseModel, Field
from datetime import datetime

from sqlalchemy import BigInteger, String, TIMESTAMP, text, select, func
from sqlalchemy.orm import declarative_base, Mapped, mapped_column
from sqlalchemy.ext.asyncio import AsyncSession

from utils import ResponseService
from utils.biz_code import NOT_FOUND, DB_CREATE, DB_UPDATE, DB_DELETE, INVALID_PAGE, ERR_INTERNAL
from configs.db import get_session
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

Base = declarative_base()
router = APIRouter(prefix="/albums", tags=["albums"])


# ORM model 对应你的表结构
class Album(Base):
    __tablename__ = "albums"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    author: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    liked: Mapped[int] = mapped_column(BigInteger, server_default=text("0"), nullable=False)
    name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP,
        server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"),
        nullable=False,
    )


# Pydantic schemas
class AlbumBase(BaseModel):
    name: Optional[str] = None
    author: Optional[str] = None
    description: Optional[str] = None
    liked: Optional[int] = Field(default=0, ge=0)


class AlbumCreate(AlbumBase):
    pass


class AlbumUpdate(BaseModel):
    name: Optional[str] = None
    author: Optional[str] = None
    description: Optional[str] = None
    liked: Optional[int] = Field(default=None, ge=0)


class AlbumOut(AlbumBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: int(v.timestamp()) if v else None
        }


# CRUD endpoints

@router.post("", status_code=status.HTTP_201_CREATED)
async def create_album(payload: AlbumCreate, session: AsyncSession = Depends(get_session)):
    """Create a new album"""
    try:
        album = Album(
            name=payload.name,
            author=payload.author,
            description=payload.description,
            liked=payload.liked or 0,
        )
        session.add(album)
        await session.commit()
        await session.refresh(album)
        
        album_data = AlbumOut.from_orm(album).model_dump(mode='json')
        return ResponseService.created(data=album_data)
    except IntegrityError as e:
        await session.rollback()
        return ResponseService.internal_error("数据完整性错误", DB_CREATE)
    except SQLAlchemyError as e:
        await session.rollback()
        return ResponseService.internal_error("创建专辑失败", DB_CREATE)
    except Exception as e:
        await session.rollback()
        raise ResponseService.Error(biz_code=ERR_INTERNAL, details={"message": "创建专辑时发生未知错误"})


@router.get("")
async def list_albums(limit: int = 100, offset: int = 0, session: AsyncSession = Depends(get_session)):
    """List all albums with pagination"""
    try:
        if limit <= 0 or limit > 1000:
            raise ResponseService.Error(biz_code=INVALID_PAGE, details={"message": "Limit必须在1到1000之间"})
        if offset < 0:
            raise ResponseService.Error(biz_code=INVALID_PAGE, details={"message": "Offset必须为非负数"})
        
        # Get total count
        count_stmt = select(func.count()).select_from(Album)
        count_result = await session.execute(count_stmt)
        total = count_result.scalar()
        
        # Get paginated data
        stmt = select(Album).limit(limit).offset(offset)
        result = await session.execute(stmt)
        albums = result.scalars().all()
        
        albums_data = [AlbumOut.from_orm(album).model_dump(mode='json') for album in albums]
        return ResponseService.success(data={"items": albums_data, "total": total})
    except ResponseService.Error:
        raise
    except SQLAlchemyError as e:
        import traceback
        traceback.print_exc()
        return ResponseService.internal_error("查询专辑列表失败", ERR_INTERNAL)
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise ResponseService.Error(biz_code=ERR_INTERNAL, details={"message": "查询专辑列表时发生未知错误"})


@router.get("/{album_id}")
async def get_album(album_id: int, session: AsyncSession = Depends(get_session)):
    """Get a specific album by ID"""
    try:
        if album_id <= 0:
            return ResponseService.bad_request("Invalid album_id: 必须为正数")
        
        album = await session.get(Album, album_id)
        if not album:
            return ResponseService.not_found(f"ID为{album_id}的专辑不存在", NOT_FOUND)
        
        album_data = AlbumOut.from_orm(album).model_dump(mode='json')
        return ResponseService.success(data=album_data)
    except ResponseService.Error:
        raise
    except SQLAlchemyError as e:
        import traceback
        traceback.print_exc()
        return ResponseService.internal_error("查询专辑失败", ERR_INTERNAL)
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise ResponseService.Error(biz_code=ERR_INTERNAL, details={"message": "查询专辑时发生未知错误"})


@router.put("/{album_id}")
async def update_album(album_id: int, payload: AlbumUpdate, session: AsyncSession = Depends(get_session)):
    """Update an album by ID"""
    try:
        if album_id <= 0:
            return ResponseService.bad_request("Invalid album_id: 必须为正数")
        
        album = await session.get(Album, album_id)
        if not album:
            return ResponseService.not_found(f"ID为{album_id}的专辑不存在", NOT_FOUND)

        # Check if at least one field is provided
        if all(v is None for v in [payload.name, payload.author, payload.description, payload.liked]):
            return ResponseService.bad_request("至少需要提供一个字段进行更新")

        if payload.name is not None:
            album.name = payload.name
        if payload.author is not None:
            album.author = payload.author
        if payload.description is not None:
            album.description = payload.description
        if payload.liked is not None:
            album.liked = payload.liked

        session.add(album)
        await session.commit()
        await session.refresh(album)
        
        album_data = AlbumOut.from_orm(album).model_dump(mode='json')
        return ResponseService.updated(data=album_data)
    except ResponseService.Error:
        raise
    except IntegrityError as e:
        await session.rollback()
        return ResponseService.internal_error("数据完整性错误", DB_UPDATE)
    except SQLAlchemyError as e:
        await session.rollback()
        return ResponseService.internal_error("更新专辑失败", DB_UPDATE)
    except Exception as e:
        await session.rollback()
        raise ResponseService.Error(biz_code=ERR_INTERNAL, details={"message": "更新专辑时发生未知错误"})


@router.delete("/{album_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_album(album_id: int, session: AsyncSession = Depends(get_session)):
    """Delete an album by ID (will cascade delete all songs)"""
    try:
        if album_id <= 0:
            return ResponseService.bad_request("Invalid album_id: 必须为正数")
        
        album = await session.get(Album, album_id)
        if not album:
            return ResponseService.not_found(f"ID为{album_id}的专辑不存在", NOT_FOUND)
        
        await session.delete(album)
        await session.commit()
        return ResponseService.deleted()
    except ResponseService.Error:
        raise
    except SQLAlchemyError as e:
        await session.rollback()
        return ResponseService.internal_error("删除专辑失败", DB_DELETE)
    except Exception as e:
        await session.rollback()
        raise ResponseService.Error(biz_code=ERR_INTERNAL, details={"message": "删除专辑时发生未知错误"})
