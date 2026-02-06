from typing import Optional, Tuple, List

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from models.album import Album
from schemas.album import AlbumCreate, AlbumUpdate


async def create_album(session: AsyncSession, payload: AlbumCreate) -> Album:
    """
    Create a new album and persist it to the database.
    """
    album = Album(
        name=payload.name,
        author=payload.author,
        description=payload.description,
        liked=payload.liked if payload.liked is not None else 0,
    )
    session.add(album)
    await session.commit()
    await session.refresh(album)
    return album


async def list_albums(
    session: AsyncSession,
    *,
    limit: int,
    offset: int,
    name: Optional[str] = None,
    author: Optional[str] = None,
    min_liked: Optional[int] = None,
    max_liked: Optional[int] = None,
) -> Tuple[List[Album], int]:
    """
    List albums with optional filters and pagination.
    Assumes basic parameter validation (limit/offset ranges etc.) is done by the caller.
    """
    conditions = []
    if name:
        conditions.append(Album.name.ilike(f"%{name}%"))
    if author:
        conditions.append(Album.author.ilike(f"%{author}%"))
    if min_liked is not None:
        conditions.append(Album.liked >= min_liked)
    if max_liked is not None:
        conditions.append(Album.liked <= max_liked)

    # total count
    count_stmt = select(func.count()).select_from(Album)
    if conditions:
        count_stmt = count_stmt.where(*conditions)
    count_result = await session.execute(count_stmt)
    total = count_result.scalar() or 0

    # page data
    stmt = select(Album)
    if conditions:
        stmt = stmt.where(*conditions)
    stmt = stmt.limit(limit).offset(offset)
    result = await session.execute(stmt)
    albums = result.scalars().all()

    return albums, total


async def get_album_by_id(session: AsyncSession, album_id: int) -> Optional[Album]:
    """
    Fetch a single album by primary key.
    """
    return await session.get(Album, album_id)


async def update_album(
    session: AsyncSession,
    album: Album,
    payload: AlbumUpdate,
) -> Album:
    """
    Update an existing album instance with the provided payload and persist changes.
    Assumes that payload has at least one field set and album exists.
    """
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
    return album


async def delete_album(session: AsyncSession, album: Album) -> None:
    """
    Delete the given album from the database.
    """
    await session.delete(album)
    await session.commit()


