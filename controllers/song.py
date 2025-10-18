from typing import Optional

from fastapi import APIRouter, Depends, status
from pydantic import BaseModel, Field
from datetime import datetime

from sqlalchemy import BigInteger, String, TIMESTAMP, Integer, ForeignKey, text, select, func
from sqlalchemy.orm import declarative_base, Mapped, mapped_column

from sqlalchemy.ext.asyncio import AsyncSession

from utils.restful import success, created, updated, deleted, not_found, bad_request, db_error, BusinessError
from utils.biz_code import NOT_FOUND, BAD_REQUEST as BIZ_BAD_REQUEST, DB_CREATE, DB_UPDATE, DB_DELETE
from configs.db import get_session
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

Base = declarative_base()
router = APIRouter(prefix="/songs", tags=["songs"])


# ORM model for songs table
class Song(Base):
    __tablename__ = "songs"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    album_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("albums.id", ondelete="CASCADE"), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    duration: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    track_number: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP,
        server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"),
        nullable=False,
    )


# Pydantic schemas
class SongBase(BaseModel):
    album_id: int = Field(..., description="Album ID (foreign key)")
    title: str = Field(..., min_length=1, max_length=255, description="Song title")
    duration: Optional[int] = Field(default=None, ge=0, description="Duration in seconds")
    track_number: Optional[int] = Field(default=None, ge=1, description="Track number in album")


class SongCreate(SongBase):
    pass


class SongUpdate(BaseModel):
    album_id: Optional[int] = Field(default=None, description="Album ID (foreign key)")
    title: Optional[str] = Field(default=None, min_length=1, max_length=255, description="Song title")
    duration: Optional[int] = Field(default=None, ge=0, description="Duration in seconds")
    track_number: Optional[int] = Field(default=None, ge=1, description="Track number in album")


class SongOut(BaseModel):
    id: int
    album_id: int
    title: str
    duration: Optional[int]
    track_number: Optional[int]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: int(v.timestamp()) if v else None
        }


# CRUD endpoints

@router.post("", status_code=status.HTTP_201_CREATED)
async def create_song(payload: SongCreate, session: AsyncSession = Depends(get_session)):
    """Create a new song"""
    try:
        song = Song(
            album_id=payload.album_id,
            title=payload.title,
            duration=payload.duration,
            track_number=payload.track_number,
        )
        session.add(song)
        await session.commit()
        await session.refresh(song)
        
        # Convert ORM object to Pydantic model and serialize properly
        song_data = SongOut.from_orm(song).model_dump(mode='json')
        return created(data=song_data)
    except IntegrityError as e:
        await session.rollback()
        # Foreign key constraint violation
        if "foreign key constraint" in str(e).lower() or "cannot add or update a child row" in str(e).lower():
            return bad_request(
                biz_code=BIZ_BAD_REQUEST,
                errors={"message": f"ID为{payload.album_id}的专辑不存在"}
            )
        return db_error(biz_code=DB_CREATE, errors={"message": "数据完整性错误"})
    except SQLAlchemyError as e:
        await session.rollback()
        return db_error(biz_code=DB_CREATE, errors={"message": "创建歌曲失败"})
    except Exception as e:
        await session.rollback()
        raise BusinessError(biz_code=5000, details={"message": "创建歌曲时发生未知错误"})


@router.get("")
async def list_songs(
    album_id: Optional[int] = None,
    limit: int = 100,
    offset: int = 0,
    session: AsyncSession = Depends(get_session)
):
    """List all songs, optionally filtered by album_id"""
    try:
        # Build base query for filtering
        base_stmt = select(Song)
        if album_id is not None:
            base_stmt = base_stmt.where(Song.album_id == album_id)
        
        # Get total count with same filter
        count_stmt = select(func.count()).select_from(Song)
        if album_id is not None:
            count_stmt = count_stmt.where(Song.album_id == album_id)
        count_result = await session.execute(count_stmt)
        total = count_result.scalar()
        
        # Get paginated data
        stmt = base_stmt.limit(limit).offset(offset)
        result = await session.execute(stmt)
        songs = result.scalars().all()
        
        # Convert ORM objects to Pydantic models and serialize properly
        songs_data = [SongOut.from_orm(song).model_dump(mode='json') for song in songs]
        return success(data={"items": songs_data, "total": total})
    except SQLAlchemyError as e:
        import traceback
        traceback.print_exc()
        return db_error(errors={"message": "查询歌曲列表失败"})
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise BusinessError(biz_code=5000, details={"message": "查询歌曲列表时发生未知错误"})


@router.get("/album/{album_id}")
async def get_songs_by_album(album_id: int, session: AsyncSession = Depends(get_session)):
    """Get all songs for a specific album"""
    try:
        if album_id <= 0:
            raise BusinessError(biz_code=BIZ_BAD_REQUEST, details={"message": "Invalid album_id: 必须为正数"})
        
        stmt = select(Song).where(Song.album_id == album_id).order_by(Song.track_number)
        result = await session.execute(stmt)
        songs = result.scalars().all()
        
        # Convert ORM objects to Pydantic models and serialize properly
        songs_data = [SongOut.from_orm(song).model_dump(mode='json') for song in songs]
        return success(data=songs_data)
    except BusinessError:
        raise
    except SQLAlchemyError as e:
        import traceback
        traceback.print_exc()
        return db_error(errors={"message": "查询专辑歌曲失败"})
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise BusinessError(biz_code=5000, details={"message": "查询专辑歌曲时发生未知错误"})


@router.get("/{song_id}")
async def get_song(song_id: int, session: AsyncSession = Depends(get_session)):
    """Get a specific song by ID"""
    try:
        if song_id <= 0:
            raise BusinessError(biz_code=BIZ_BAD_REQUEST, details={"message": "Invalid song_id: 必须为正数"})
        
        song = await session.get(Song, song_id)
        if not song:
            return not_found(biz_code=NOT_FOUND, errors={"message": f"ID为{song_id}的歌曲不存在"})
        
        # Convert ORM object to Pydantic model and serialize properly
        song_data = SongOut.from_orm(song).model_dump(mode='json')
        return success(data=song_data)
    except BusinessError:
        raise
    except SQLAlchemyError as e:
        import traceback
        traceback.print_exc()
        return db_error(errors={"message": "查询歌曲失败"})
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise BusinessError(biz_code=5000, details={"message": "查询歌曲时发生未知错误"})


@router.put("/{song_id}")
async def update_song(song_id: int, payload: SongUpdate, session: AsyncSession = Depends(get_session)):
    """Update a song by ID"""
    try:
        if song_id <= 0:
            raise BusinessError(biz_code=BIZ_BAD_REQUEST, details={"message": "Invalid song_id: 必须为正数"})
        
        song = await session.get(Song, song_id)
        if not song:
            return not_found(biz_code=NOT_FOUND, errors={"message": f"ID为{song_id}的歌曲不存在"})

        # Check if at least one field is provided
        if all(v is None for v in [payload.album_id, payload.title, payload.duration, payload.track_number]):
            raise BusinessError(biz_code=BIZ_BAD_REQUEST, details={"message": "至少需要提供一个字段进行更新"})

        if payload.album_id is not None:
            song.album_id = payload.album_id
        if payload.title is not None:
            song.title = payload.title
        if payload.duration is not None:
            song.duration = payload.duration
        if payload.track_number is not None:
            song.track_number = payload.track_number

        session.add(song)
        await session.commit()
        await session.refresh(song)
        
        # Convert ORM object to Pydantic model and serialize properly
        song_data = SongOut.from_orm(song).model_dump(mode='json')
        return updated(data=song_data)
    except BusinessError:
        raise
    except IntegrityError as e:
        await session.rollback()
        if "foreign key constraint" in str(e).lower():
            return bad_request(
                biz_code=BIZ_BAD_REQUEST,
                errors={"message": f"ID为{payload.album_id}的专辑不存在"}
            )
        return db_error(biz_code=DB_UPDATE, errors={"message": "数据完整性错误"})
    except SQLAlchemyError as e:
        await session.rollback()
        return db_error(biz_code=DB_UPDATE, errors={"message": "更新歌曲失败"})
    except Exception as e:
        await session.rollback()
        raise BusinessError(biz_code=5000, details={"message": "更新歌曲时发生未知错误"})


@router.delete("/{song_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_song(song_id: int, session: AsyncSession = Depends(get_session)):
    """Delete a song by ID"""
    try:
        if song_id <= 0:
            raise BusinessError(biz_code=BIZ_BAD_REQUEST, details={"message": "Invalid song_id: 必须为正数"})
        
        song = await session.get(Song, song_id)
        if not song:
            return not_found(biz_code=NOT_FOUND, errors={"message": f"ID为{song_id}的歌曲不存在"})
        
        await session.delete(song)
        await session.commit()
        return deleted()
    except BusinessError:
        raise
    except SQLAlchemyError as e:
        await session.rollback()
        return db_error(biz_code=DB_DELETE, errors={"message": "删除歌曲失败"})
    except Exception as e:
        await session.rollback()
        raise BusinessError(biz_code=5000, details={"message": "删除歌曲时发生未知错误"})
