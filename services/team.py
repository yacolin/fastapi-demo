from typing import Optional, Tuple, List

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from models.team import Team
from schemas.team import TeamCreate, TeamUpdate


async def create_team(session: AsyncSession, payload: TeamCreate) -> Team:
    """
    Create a new team and persist it to the database.
    """
    team = Team(
        name=payload.name,
        city=payload.city,
        divide=payload.divide,
        part=payload.part,
        champions=payload.champions or 0,
        logo=payload.logo,
    )
    session.add(team)
    await session.commit()
    await session.refresh(team)
    return team


async def list_teams(
    session: AsyncSession,
    *,
    limit: int,
    offset: int,
    city: Optional[str] = None,
    divide: Optional[str] = None,
    part: Optional[str] = None,
) -> Tuple[List[Team], int]:
    """
    List teams with optional filters and pagination.
    """
    conditions = []
    if city is not None:
        conditions.append(Team.city == city)
    if divide is not None:
        conditions.append(Team.divide == divide)
    if part is not None:
        conditions.append(Team.part == part)

    # total count
    count_stmt = select(func.count()).select_from(Team)
    if conditions:
        count_stmt = count_stmt.where(*conditions)
    count_result = await session.execute(count_stmt)
    total = count_result.scalar() or 0

    # page data
    stmt = select(Team)
    if conditions:
        stmt = stmt.where(*conditions)
    stmt = stmt.limit(limit).offset(offset)
    result = await session.execute(stmt)
    teams = result.scalars().all()

    return teams, total


async def get_team_by_id(session: AsyncSession, team_id: int) -> Optional[Team]:
    """
    Fetch a single team by primary key.
    """
    return await session.get(Team, team_id)


async def update_team(
    session: AsyncSession,
    team: Team,
    payload: TeamUpdate,
) -> Team:
    """
    Update an existing team instance with the provided payload and persist changes.
    Assumes that payload has at least one field set and team exists.
    """
    if payload.name is not None:
        team.name = payload.name
    if payload.city is not None:
        team.city = payload.city
    if payload.divide is not None:
        team.divide = payload.divide
    if payload.part is not None:
        team.part = payload.part
    if payload.champions is not None:
        team.champions = payload.champions
    if payload.logo is not None:
        team.logo = payload.logo

    session.add(team)
    await session.commit()
    await session.refresh(team)
    return team


async def delete_team(session: AsyncSession, team: Team) -> None:
    """
    Delete the given team from the database.
    """
    await session.delete(team)
    await session.commit()
