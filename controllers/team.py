from typing import Optional

from fastapi import APIRouter, Depends, status
from pydantic import BaseModel, Field
from datetime import datetime

from sqlalchemy import Integer, String, TIMESTAMP, text, select, func
from sqlalchemy.orm import declarative_base, Mapped, mapped_column

from sqlalchemy.ext.asyncio import AsyncSession

from utils import ResponseService
from utils.biz_code import BizCode
from configs import get_session
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

Base = declarative_base()
router = APIRouter(prefix="/teams", tags=["teams"])


# ORM model for teams table
class Team(Base):
    __tablename__ = "teams"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    champions: Mapped[int] = mapped_column(Integer, server_default=text("0"), nullable=True)
    city: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"), nullable=False)
    divide: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    logo: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    part: Mapped[Optional[str]] = mapped_column(String(1), nullable=True)
    updated_at: Mapped[Optional[datetime]] = mapped_column(
        TIMESTAMP,
        server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"),
        nullable=True,
    )


# Pydantic schemas
class TeamBase(BaseModel):
    name: Optional[str] = Field(default=None, max_length=255, description="Team name")
    city: Optional[str] = Field(default=None, max_length=255, description="City")
    divide: Optional[str] = Field(default=None, max_length=255, description="Division")
    part: Optional[str] = Field(default=None, max_length=1, description="Conference part (E/W)")
    champions: Optional[int] = Field(default=0, ge=0, description="Number of championships")
    logo: Optional[str] = Field(default=None, max_length=255, description="Logo URL")


class TeamCreate(TeamBase):
    pass


class TeamUpdate(BaseModel):
    name: Optional[str] = Field(default=None, max_length=255, description="Team name")
    city: Optional[str] = Field(default=None, max_length=255, description="City")
    divide: Optional[str] = Field(default=None, max_length=255, description="Division")
    part: Optional[str] = Field(default=None, max_length=1, description="Conference part (E/W)")
    champions: Optional[int] = Field(default=None, ge=0, description="Number of championships")
    logo: Optional[str] = Field(default=None, max_length=255, description="Logo URL")


class TeamOut(BaseModel):
    id: int
    name: Optional[str]
    city: Optional[str]
    divide: Optional[str]
    part: Optional[str]
    champions: int
    logo: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: int(v.timestamp()) if v else None
        }


# CRUD endpoints

@router.post("", status_code=status.HTTP_201_CREATED)
async def create_team(payload: TeamCreate, session: AsyncSession = Depends(get_session)):
    """Create a new team"""
    try:
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
        
        team_data = TeamOut.from_orm(team).model_dump(mode='json')
        return ResponseService.created(data=team_data)
    except IntegrityError as e:
        await session.rollback()
        return ResponseService.db_error("数据完整性错误", BizCode.DB_CREATE)
    except SQLAlchemyError as e:
        await session.rollback()
        return ResponseService.db_error("创建球队失败", BizCode.DB_CREATE)
    except Exception as e:
        await session.rollback()
        raise ResponseService.Error(biz_code=BizCode.ERR_INTERNAL, details={"message": "创建球队时发生未知错误"})


@router.get("")
async def list_teams(
    city: Optional[str] = None,
    divide: Optional[str] = None,
    part: Optional[str] = None,
    limit: int = 100,
    offset: int = 0,
    session: AsyncSession = Depends(get_session)
):
    """List all teams with optional filters"""
    try:
        if limit <= 0 or limit > 1000:
            raise ResponseService.Error(biz_code=BizCode.INVALID_PAGE, details={"message": "Limit必须在1到1000之间"})
        if offset < 0:
            raise ResponseService.Error(biz_code=BizCode.INVALID_PAGE, details={"message": "Offset必须为非负数"})
        
        # Build base query for filtering
        base_stmt = select(Team)
        if city is not None:
            base_stmt = base_stmt.where(Team.city == city)
        if divide is not None:
            base_stmt = base_stmt.where(Team.divide == divide)
        if part is not None:
            base_stmt = base_stmt.where(Team.part == part)
        
        # Get total count with same filter
        count_stmt = select(func.count()).select_from(Team)
        if city is not None:
            count_stmt = count_stmt.where(Team.city == city)
        if divide is not None:
            count_stmt = count_stmt.where(Team.divide == divide)
        if part is not None:
            count_stmt = count_stmt.where(Team.part == part)
        count_result = await session.execute(count_stmt)
        total = count_result.scalar()
        
        # Get paginated data
        stmt = base_stmt.limit(limit).offset(offset)
        result = await session.execute(stmt)
        teams = result.scalars().all()
        
        teams_data = [TeamOut.from_orm(team).model_dump(mode='json') for team in teams]
        return ResponseService.success(data={"items": teams_data, "total": total})
    except ResponseService.Error:
        raise
    except SQLAlchemyError as e:
        import traceback
        traceback.print_exc()
        return ResponseService.internal_error("查询球队列表失败", BizCode.ERR_INTERNAL)
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise ResponseService.Error(biz_code=BizCode.ERR_INTERNAL, details={"message": "查询球队列表时发生未知错误"})


@router.get("/{team_id}")
async def get_team(team_id: int, session: AsyncSession = Depends(get_session)):
    """Get a specific team by ID"""
    try:
        if team_id <= 0:
            return ResponseService.bad_request("Invalid team_id: 必须为正数")
        
        team = await session.get(Team, team_id)
        if not team:
            return ResponseService.not_found(f"ID为{team_id}的球队不存在", BizCode.NOT_FOUND)
        
        team_data = TeamOut.from_orm(team).model_dump(mode='json')
        return ResponseService.success(data=team_data)
    except ResponseService.Error:
        raise
    except SQLAlchemyError as e:
        import traceback
        traceback.print_exc()
        return ResponseService.internal_error("查询球队失败", BizCode.ERR_INTERNAL)
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise ResponseService.Error(biz_code=BizCode.ERR_INTERNAL, details={"message": "查询球队时发生未知错误"})


@router.put("/{team_id}")
async def update_team(team_id: int, payload: TeamUpdate, session: AsyncSession = Depends(get_session)):
    """Update a team by ID"""
    try:
        if team_id <= 0:
            return ResponseService.bad_request("Invalid team_id: 必须为正数")
        
        team = await session.get(Team, team_id)
        if not team:
            return ResponseService.not_found(f"ID为{team_id}的球队不存在", BizCode.NOT_FOUND)

        # Check if at least one field is provided
        if not payload.model_dump(exclude_unset=True):
            return ResponseService.bad_request("至少需要提供一个字段进行更新")

        # Update the team with the provided payload (using the payload model)
        for key, value in payload.model_dump(exclude_unset=True).items():
            setattr(team, key, value)

        session.add(team)
        await session.commit()
        await session.refresh(team)
        
        team_data = TeamOut.from_orm(team).model_dump(mode='json')
        return ResponseService.updated(data=team_data)
    except ResponseService.Error:
        raise
    except IntegrityError as e:
        await session.rollback()
        return ResponseService.db_error("数据完整性错误", BizCode.DB_UPDATE)
    except SQLAlchemyError as e:
        await session.rollback()
        return ResponseService.db_error("更新球队失败", BizCode.DB_UPDATE)
    except Exception as e:
        await session.rollback()
        raise ResponseService.Error(biz_code=BizCode.ERR_INTERNAL, details={"message": "更新球队时发生未知错误"})


@router.delete("/{team_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_team(team_id: int, session: AsyncSession = Depends(get_session)):
    """Delete a team by ID"""
    try:
        if team_id <= 0:
            return ResponseService.bad_request("Invalid team_id: 必须为正数")
        
        team = await session.get(Team, team_id)
        if not team:
            return ResponseService.not_found(f"ID为{team_id}的球队不存在", BizCode.NOT_FOUND)
        
        await session.delete(team)
        await session.commit()
        return ResponseService.deleted()
    except ResponseService.Error:
        raise
    except SQLAlchemyError as e:
        await session.rollback()
        return ResponseService.db_error("删除球队失败", BizCode.DB_DELETE)
    except Exception as e:
        await session.rollback()
        raise ResponseService.Error(biz_code=BizCode.ERR_INTERNAL, details={"message": "删除球队时发生未知错误"})
