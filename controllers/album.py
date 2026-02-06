from typing import Optional

from fastapi import APIRouter, Depends, status

from sqlalchemy.ext.asyncio import AsyncSession

from utils import ResponseService
from utils.biz_code import BizCode
from configs.db import get_session
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from schemas.album import AlbumCreate, AlbumUpdate, AlbumOut
from services import album as album_service


router = APIRouter(prefix="/albums", tags=["albums"])


# CRUD endpoints

@router.post("", status_code=status.HTTP_201_CREATED)
async def create_album(payload: AlbumCreate, session: AsyncSession = Depends(get_session)):
    """Create a new album"""
    try:
        album = await album_service.create_album(session=session, payload=payload)

        album_data = AlbumOut.model_validate(album).model_dump(mode='json')
        return ResponseService.created(data=album_data)
    except IntegrityError as e:
        await session.rollback()
        return ResponseService.db_error("数据完整性错误", BizCode.DB_CREATE)
    except SQLAlchemyError as e:
        await session.rollback()
        return ResponseService.db_error("创建专辑失败", BizCode.DB_CREATE)
    except Exception as e:
        await session.rollback()
        raise ResponseService.Error(biz_code=BizCode.ERR_INTERNAL, details={"message": "创建专辑时发生未知错误"})


@router.get("")
async def list_albums(
    limit: int = 100,
    offset: int = 0,
    name: Optional[str] = None,
    author: Optional[str] = None,
    min_liked: Optional[int] = None,
    max_liked: Optional[int] = None,
    session: AsyncSession = Depends(get_session),
):
    """List all albums with pagination and optional filters"""
    try:
        if limit <= 0 or limit > 1000:
            raise ResponseService.Error(biz_code=BizCode.INVALID_PAGE, details={"message": "Limit必须在1到1000之间"})
        if offset < 0:
            raise ResponseService.Error(biz_code=BizCode.INVALID_PAGE, details={"message": "Offset必须为非负数"})
        if min_liked is not None and min_liked < 0:
            return ResponseService.bad_request("min_liked 必须为非负数")
        if max_liked is not None and max_liked < 0:
            return ResponseService.bad_request("max_liked 必须为非负数")
        if min_liked is not None and max_liked is not None and min_liked > max_liked:
            return ResponseService.bad_request("min_liked 不能大于 max_liked")

        albums, total = await album_service.list_albums(
            session=session,
            limit=limit,
            offset=offset,
            name=name,
            author=author,
            min_liked=min_liked,
            max_liked=max_liked,
        )

        albums_data = [AlbumOut.model_validate(album).model_dump(mode='json') for album in albums]
        return ResponseService.success(data={"items": albums_data, "total": total})
    except ResponseService.Error:
        raise
    except SQLAlchemyError as e:
        import traceback
        traceback.print_exc()
        return ResponseService.internal_error("查询专辑列表失败", BizCode.ERR_INTERNAL)
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise ResponseService.Error(biz_code=BizCode.ERR_INTERNAL, details={"message": "查询专辑列表时发生未知错误"})


@router.get("/{album_id}")
async def get_album(album_id: int, session: AsyncSession = Depends(get_session)):
    """Get a specific album by ID"""
    try:
        if album_id <= 0:
            return ResponseService.bad_request("Invalid album_id: 必须为正数")

        album = await album_service.get_album_by_id(session=session, album_id=album_id)
        if not album:
            return ResponseService.not_found(f"ID为{album_id}的专辑不存在", BizCode.NOT_FOUND)
        
        album_data = AlbumOut.model_validate(album).model_dump(mode='json')
        return ResponseService.success(data=album_data)
    except ResponseService.Error:
        raise
    except SQLAlchemyError as e:
        import traceback
        traceback.print_exc()
        return ResponseService.internal_error("查询专辑失败", BizCode.ERR_INTERNAL)
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise ResponseService.Error(biz_code=BizCode.ERR_INTERNAL, details={"message": "查询专辑时发生未知错误"})


@router.put("/{album_id}")
async def update_album(album_id: int, payload: AlbumUpdate, session: AsyncSession = Depends(get_session)):
    """Update an album by ID"""
    try:
        if album_id <= 0:
            return ResponseService.bad_request("Invalid album_id: 必须为正数")

        album = await album_service.get_album_by_id(session=session, album_id=album_id)
        if not album:
            return ResponseService.not_found(f"ID为{album_id}的专辑不存在", BizCode.NOT_FOUND)

        # Check if at least one field is provided
        if all(v is None for v in [payload.name, payload.author, payload.description, payload.liked]):
            return ResponseService.bad_request("至少需要提供一个字段进行更新")

        album = await album_service.update_album(session=session, album=album, payload=payload)

        album_data = AlbumOut.model_validate(album).model_dump(mode='json')
        return ResponseService.updated(data=album_data)
    except ResponseService.Error:
        raise
    except IntegrityError as e:
        await session.rollback()
        return ResponseService.db_error("数据完整性错误", BizCode.DB_UPDATE)
    except SQLAlchemyError as e:
        await session.rollback()
        return ResponseService.db_error("更新专辑失败", BizCode.DB_UPDATE)
    except Exception as e:
        await session.rollback()
        raise ResponseService.Error(biz_code=BizCode.ERR_INTERNAL, details={"message": "更新专辑时发生未知错误"})


@router.delete("/{album_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_album(album_id: int, session: AsyncSession = Depends(get_session)):
    """Delete an album by ID (will cascade delete all songs)"""
    try:
        if album_id <= 0:
            return ResponseService.bad_request("Invalid album_id: 必须为正数")

        album = await album_service.get_album_by_id(session=session, album_id=album_id)
        if not album:
            return ResponseService.not_found(f"ID为{album_id}的专辑不存在", BizCode.NOT_FOUND)
        
        await album_service.delete_album(session=session, album=album)
        return ResponseService.deleted()
    except ResponseService.Error:
        raise
    except SQLAlchemyError as e:
        await session.rollback()
        return ResponseService.db_error("删除专辑失败", BizCode.DB_DELETE)
    except Exception as e:
        await session.rollback()
        raise ResponseService.Error(biz_code=BizCode.ERR_INTERNAL, details={"message": "删除专辑时发生未知错误"})
