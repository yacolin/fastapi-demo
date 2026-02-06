from typing import Optional

from fastapi import APIRouter, Depends, status

from sqlalchemy.ext.asyncio import AsyncSession

from utils import ResponseService
from utils.biz_code import BizCode
from configs.db import get_session
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from schemas.song import SongCreate, SongUpdate, SongOut
from services import song as song_service


router = APIRouter(prefix="/songs", tags=["songs"])


# CRUD endpoints

@router.post("", status_code=status.HTTP_201_CREATED)
async def create_song(payload: SongCreate, session: AsyncSession = Depends(get_session)):
    """Create a new song"""
    try:
        song = await song_service.create_song(session=session, payload=payload)

        song_data = SongOut.model_validate(song).model_dump(mode='json')
        return ResponseService.created(data=song_data)
    except IntegrityError as e:
        await session.rollback()
        # Foreign key constraint violation
        if "foreign key constraint" in str(e).lower() or "cannot add or update a child row" in str(e).lower():
            return ResponseService.bad_request(f"ID为{payload.album_id}的专辑不存在")
        return ResponseService.db_error("数据完整性错误", BizCode.DB_CREATE)
    except SQLAlchemyError as e:
        await session.rollback()
        return ResponseService.db_error("创建歌曲失败", BizCode.DB_CREATE)
    except Exception as e:
        await session.rollback()
        raise ResponseService.Error(biz_code=BizCode.ERR_INTERNAL, details={
                                    "message": "创建歌曲时发生未知错误"})


@router.get("")
async def list_songs(
    album_id: Optional[int] = None,
    limit: int = 100,
    offset: int = 0,
    session: AsyncSession = Depends(get_session)
):
    """List all songs, optionally filtered by album_id"""
    try:
        songs, total = await song_service.list_songs(
            session=session,
            limit=limit,
            offset=offset,
            album_id=album_id,
        )

        songs_data = [SongOut.model_validate(song).model_dump(
            mode='json') for song in songs]
        return ResponseService.success(data={"items": songs_data, "total": total})
    except SQLAlchemyError as e:
        import traceback
        traceback.print_exc()
        return ResponseService.internal_error("查询歌曲列表失败", BizCode.ERR_INTERNAL)
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise ResponseService.Error(biz_code=BizCode.ERR_INTERNAL, details={
                                    "message": "查询歌曲列表时发生未知错误"})


@router.get("/album/{album_id}")
async def get_songs_by_album(album_id: int, session: AsyncSession = Depends(get_session)):
    """Get all songs for a specific album"""
    try:
        if album_id <= 0:
            return ResponseService.bad_request("Invalid album_id: 必须为正数")

        songs = await song_service.get_songs_by_album(session=session, album_id=album_id)

        songs_data = [SongOut.model_validate(song).model_dump(
            mode='json') for song in songs]
        return ResponseService.success(data=songs_data)
    except ResponseService.Error:
        raise
    except SQLAlchemyError as e:
        import traceback
        traceback.print_exc()
        return ResponseService.internal_error("查询专辑歌曲失败", BizCode.ERR_INTERNAL)
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise ResponseService.Error(biz_code=BizCode.ERR_INTERNAL, details={
                                    "message": "查询专辑歌曲时发生未知错误"})


@router.get("/{song_id}")
async def get_song(song_id: int, session: AsyncSession = Depends(get_session)):
    """Get a specific song by ID"""
    try:
        if song_id <= 0:
            return ResponseService.bad_request("Invalid song_id: 必须为正数")

        song = await song_service.get_song_by_id(session=session, song_id=song_id)
        if not song:
            return ResponseService.not_found(f"ID为{song_id}的歌曲不存在", BizCode.NOT_FOUND)

        song_data = SongOut.model_validate(song).model_dump(mode='json')
        return ResponseService.success(data=song_data)
    except ResponseService.Error:
        raise
    except SQLAlchemyError as e:
        import traceback
        traceback.print_exc()
        return ResponseService.internal_error("查询歌曲失败", BizCode.ERR_INTERNAL)
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise ResponseService.Error(biz_code=BizCode.ERR_INTERNAL, details={
                                    "message": "查询歌曲时发生未知错误"})


@router.put("/{song_id}")
async def update_song(song_id: int, payload: SongUpdate, session: AsyncSession = Depends(get_session)):
    """Update a song by ID"""
    try:
        if song_id <= 0:
            return ResponseService.bad_request("Invalid song_id: 必须为正数")

        song = await song_service.get_song_by_id(session=session, song_id=song_id)
        if not song:
            return ResponseService.not_found(f"ID为{song_id}的歌曲不存在", BizCode.NOT_FOUND)

        # Check if at least one field is provided
        if all(v is None for v in [payload.album_id, payload.title, payload.duration, payload.track_number]):
            return ResponseService.bad_request("至少需要提供一个字段进行更新")

        song = await song_service.update_song(session=session, song=song, payload=payload)

        song_data = SongOut.model_validate(song).model_dump(mode='json')
        return ResponseService.updated(data=song_data)
    except ResponseService.Error:
        raise
    except IntegrityError as e:
        await session.rollback()
        if "foreign key constraint" in str(e).lower():
            return ResponseService.bad_request(f"ID为{payload.album_id}的专辑不存在")
        return ResponseService.db_error("数据完整性错误", BizCode.DB_UPDATE)
    except SQLAlchemyError as e:
        await session.rollback()
        return ResponseService.db_error("更新歌曲失败", BizCode.DB_UPDATE)
    except Exception as e:
        await session.rollback()
        raise ResponseService.Error(biz_code=BizCode.ERR_INTERNAL, details={
                                    "message": "更新歌曲时发生未知错误"})


@router.delete("/{song_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_song(song_id: int, session: AsyncSession = Depends(get_session)):
    """Delete a song by ID"""
    try:
        if song_id <= 0:
            return ResponseService.bad_request("Invalid song_id: 必须为正数")

        song = await song_service.get_song_by_id(session=session, song_id=song_id)
        if not song:
            return ResponseService.not_found(f"ID为{song_id}的歌曲不存在", BizCode.NOT_FOUND)

        await song_service.delete_song(session=session, song=song)
        return ResponseService.deleted()
    except ResponseService.Error:
        raise
    except SQLAlchemyError as e:
        await session.rollback()
        return ResponseService.db_error("删除歌曲失败", BizCode.DB_DELETE)
    except Exception as e:
        await session.rollback()
        raise ResponseService.Error(biz_code=BizCode.ERR_INTERNAL, details={
                                    "message": "删除歌曲时发生未知错误"})
