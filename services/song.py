from typing import Optional, Tuple, List

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from models.song import Song
from schemas.song import SongCreate, SongUpdate


async def create_song(session: AsyncSession, payload: SongCreate) -> Song:
    """
    Create a new song and persist it to the database.
    """
    song = Song(
        album_id=payload.album_id,
        title=payload.title,
        duration=payload.duration,
        track_number=payload.track_number,
    )
    session.add(song)
    await session.commit()
    await session.refresh(song)
    return song


async def list_songs(
    session: AsyncSession,
    *,
    limit: int,
    offset: int,
    album_id: Optional[int] = None,
) -> Tuple[List[Song], int]:
    """
    List songs with optional filters and pagination.
    """
    conditions = []
    if album_id is not None:
        conditions.append(Song.album_id == album_id)

    # total count
    count_stmt = select(func.count()).select_from(Song)
    if conditions:
        count_stmt = count_stmt.where(*conditions)
    count_result = await session.execute(count_stmt)
    total = count_result.scalar() or 0

    # page data
    stmt = select(Song)
    if conditions:
        stmt = stmt.where(*conditions)
    stmt = stmt.limit(limit).offset(offset)
    result = await session.execute(stmt)
    songs = result.scalars().all()

    return songs, total


async def get_songs_by_album(session: AsyncSession, album_id: int) -> List[Song]:
    """
    Get all songs for a specific album.
    """
    stmt = select(Song).where(Song.album_id ==
                              album_id).order_by(Song.track_number)
    result = await session.execute(stmt)
    return result.scalars().all()


async def get_song_by_id(session: AsyncSession, song_id: int) -> Optional[Song]:
    """
    Fetch a single song by primary key.
    """
    return await session.get(Song, song_id)


async def update_song(
    session: AsyncSession,
    song: Song,
    payload: SongUpdate,
) -> Song:
    """
    Update an existing song instance with the provided payload and persist changes.
    Assumes that payload has at least one field set and song exists.
    """
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
    return song


async def delete_song(session: AsyncSession, song: Song) -> None:
    """
    Delete the given song from the database.
    """
    await session.delete(song)
    await session.commit()
