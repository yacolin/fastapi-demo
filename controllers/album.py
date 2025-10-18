from typing import Optional

from fastapi import APIRouter, Depends, status
from pydantic import BaseModel, Field
from datetime import datetime

from sqlalchemy import BigInteger, String, TIMESTAMP, text, select, func
from sqlalchemy.orm import declarative_base, Mapped, mapped_column

from sqlalchemy.ext.asyncio import AsyncSession


from utils.restful import success, created, updated, deleted, not_found, db_error, BusinessError
from utils.biz_code import NOT_FOUND, DB_CREATE, DB_UPDATE, DB_DELETE, INVALID_PAGE
from configs.db import get_session  # 使用 db.py 中的 session 依赖，避免循环导入
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
        
        # Convert ORM object to Pydantic model and serialize properly
        album_data = AlbumOut.from_orm(album).model_dump(mode='json')
        return created(data=album_data)
    except IntegrityError as e:
        await session.rollback()
        return db_error(biz_code=DB_CREATE, errors={"message": "数据完整性错误"})
    except SQLAlchemyError as e:
        await session.rollback()
        return db_error(biz_code=DB_CREATE, errors={"message": "创建专辑失败"})
    except Exception as e:
        await session.rollback()
        raise BusinessError(biz_code=5000, details={"message": "创建专辑时发生未知错误"})


@router.get("")
async def list_albums(limit: int = 100, offset: int = 0, session: AsyncSession = Depends(get_session)):
    """List all albums with pagination"""
    try:
        if limit <= 0 or limit > 1000:
            raise BusinessError(biz_code=INVALID_PAGE, details={"message": "Limit必须在1到1000之间"})
        if offset < 0:
            raise BusinessError(biz_code=INVALID_PAGE, details={"message": "Offset必须为非负数"})
        
        # Get total count
        count_stmt = select(func.count()).select_from(Album)
        count_result = await session.execute(count_stmt)
        total = count_result.scalar()
        
        # Get paginated data
        stmt = select(Album).limit(limit).offset(offset)
        result = await session.execute(stmt)
        albums = result.scalars().all()
        
        # Convert ORM objects to Pydantic models and serialize properly
        albums_data = [AlbumOut.from_orm(album).model_dump(mode='json') for album in albums]
        return success(data={"items": albums_data, "total": total})
    except BusinessError:
        raise
    except SQLAlchemyError as e:
        import traceback
        traceback.print_exc()
        return db_error(errors={"message": "查询专辑列表失败"})
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise BusinessError(biz_code=5000, details={"message": "查询专辑列表时发生未知错误"})


@router.get("/{album_id}")
async def get_album(album_id: int, session: AsyncSession = Depends(get_session)):
    """Get a specific album by ID"""
    try:
        if album_id <= 0:
            raise BusinessError(biz_code=4000, details={"message": "Invalid album_id: 必须为正数"})
        
        album = await session.get(Album, album_id)
        if not album:
            return not_found(biz_code=NOT_FOUND, errors={"message": f"ID为{album_id}的专辑不存在"})
        
        # Convert ORM object to Pydantic model and serialize properly
        album_data = AlbumOut.from_orm(album).model_dump(mode='json')
        return success(data=album_data)
    except BusinessError:
        raise
    except SQLAlchemyError as e:
        import traceback
        traceback.print_exc()
        return db_error(errors={"message": "查询专辑失败"})
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise BusinessError(biz_code=5000, details={"message": "查询专辑时发生未知错误"})


@router.put("/{album_id}")
async def update_album(album_id: int, payload: AlbumUpdate, session: AsyncSession = Depends(get_session)):
    """Update an album by ID"""
    try:
        if album_id <= 0:
            raise BusinessError(biz_code=4000, details={"message": "Invalid album_id: 必须为正数"})
        
        album = await session.get(Album, album_id)
        if not album:
            return not_found(biz_code=NOT_FOUND, errors={"message": f"ID为{album_id}的专辑不存在"})

        # Check if at least one field is provided
        if all(v is None for v in [payload.name, payload.author, payload.description, payload.liked]):
            raise BusinessError(biz_code=4000, details={"message": "至少需要提供一个字段进行更新"})

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
        
        # Convert ORM object to Pydantic model and serialize properly
        album_data = AlbumOut.from_orm(album).model_dump(mode='json')
        return updated(data=album_data)
    except BusinessError:
        raise
    except IntegrityError as e:
        await session.rollback()
        return db_error(biz_code=DB_UPDATE, errors={"message": "数据完整性错误"})
    except SQLAlchemyError as e:
        await session.rollback()
        return db_error(biz_code=DB_UPDATE, errors={"message": "更新专辑失败"})
    except Exception as e:
        await session.rollback()
        raise BusinessError(biz_code=5000, details={"message": "更新专辑时发生未知错误"})


@router.delete("/{album_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_album(album_id: int, session: AsyncSession = Depends(get_session)):
    """Delete an album by ID (will cascade delete all songs)"""
    try:
        if album_id <= 0:
            raise BusinessError(biz_code=4000, details={"message": "Invalid album_id: 必须为正数"})
        
        album = await session.get(Album, album_id)
        if not album:
            return not_found(biz_code=NOT_FOUND, errors={"message": f"ID为{album_id}的专辑不存在"})
        
        await session.delete(album)
        await session.commit()
        return deleted()
    except BusinessError:
        raise
    except SQLAlchemyError as e:
        await session.rollback()
        return db_error(biz_code=DB_DELETE, errors={"message": "删除专辑失败"})
    except Exception as e:
        await session.rollback()
        raise BusinessError(biz_code=5000, details={"message": "删除专辑时发生未知错误"})