from typing import Optional

from fastapi import APIRouter, Depends, status

from sqlalchemy.ext.asyncio import AsyncSession

from utils import ResponseService
from utils.biz_code import BizCode
from configs.db import get_session
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from schemas.team import TeamCreate, TeamUpdate, TeamOut
from services import team as team_service


router = APIRouter(prefix="/teams", tags=["teams"])


# CRUD endpoints

@router.post("", status_code=status.HTTP_201_CREATED)
async def create_team(payload: TeamCreate, session: AsyncSession = Depends(get_session)):
    """Create a new team"""
    try:
        team = await team_service.create_team(session=session, payload=payload)

        team_data = TeamOut.model_validate(team).model_dump(mode='json')
        return ResponseService.created(data=team_data)
    except IntegrityError as e:
        await session.rollback()
        return ResponseService.db_error("数据完整性错误", BizCode.DB_CREATE)
    except SQLAlchemyError as e:
        await session.rollback()
        return ResponseService.db_error("创建球队失败", BizCode.DB_CREATE)
    except Exception as e:
        await session.rollback()
        raise ResponseService.Error(biz_code=BizCode.ERR_INTERNAL, details={
                                    "message": "创建球队时发生未知错误"})


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
            raise ResponseService.Error(biz_code=BizCode.INVALID_PAGE, details={
                                        "message": "Limit必须在1到1000之间"})
        if offset < 0:
            raise ResponseService.Error(biz_code=BizCode.INVALID_PAGE, details={
                                        "message": "Offset必须为非负数"})

        teams, total = await team_service.list_teams(
            session=session,
            limit=limit,
            offset=offset,
            city=city,
            divide=divide,
            part=part,
        )

        teams_data = [TeamOut.model_validate(team).model_dump(
            mode='json') for team in teams]
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
        raise ResponseService.Error(biz_code=BizCode.ERR_INTERNAL, details={
                                    "message": "查询球队列表时发生未知错误"})


@router.get("/{team_id}")
async def get_team(team_id: int, session: AsyncSession = Depends(get_session)):
    """Get a specific team by ID"""
    try:
        if team_id <= 0:
            return ResponseService.bad_request("Invalid team_id: 必须为正数")

        team = await team_service.get_team_by_id(session=session, team_id=team_id)
        if not team:
            return ResponseService.not_found(f"ID为{team_id}的球队不存在", BizCode.NOT_FOUND)

        team_data = TeamOut.model_validate(team).model_dump(mode='json')
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
        raise ResponseService.Error(biz_code=BizCode.ERR_INTERNAL, details={
                                    "message": "查询球队时发生未知错误"})


@router.put("/{team_id}")
async def update_team(team_id: int, payload: TeamUpdate, session: AsyncSession = Depends(get_session)):
    """Update a team by ID"""
    try:
        if team_id <= 0:
            return ResponseService.bad_request("Invalid team_id: 必须为正数")

        team = await team_service.get_team_by_id(session=session, team_id=team_id)
        if not team:
            return ResponseService.not_found(f"ID为{team_id}的球队不存在", BizCode.NOT_FOUND)

        # Check if at least one field is provided
        if all(v is None for v in [payload.name, payload.city, payload.divide, payload.part, payload.champions, payload.logo]):
            return ResponseService.bad_request("至少需要提供一个字段进行更新")

        team = await team_service.update_team(session=session, team=team, payload=payload)

        team_data = TeamOut.model_validate(team).model_dump(mode='json')
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
        raise ResponseService.Error(biz_code=BizCode.ERR_INTERNAL, details={
                                    "message": "更新球队时发生未知错误"})


@router.delete("/{team_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_team(team_id: int, session: AsyncSession = Depends(get_session)):
    """Delete a team by ID"""
    try:
        if team_id <= 0:
            return ResponseService.bad_request("Invalid team_id: 必须为正数")

        team = await team_service.get_team_by_id(session=session, team_id=team_id)
        if not team:
            return ResponseService.not_found(f"ID为{team_id}的球队不存在", BizCode.NOT_FOUND)

        await team_service.delete_team(session=session, team=team)
        return ResponseService.deleted()
    except ResponseService.Error:
        raise
    except SQLAlchemyError as e:
        await session.rollback()
        return ResponseService.db_error("删除球队失败", BizCode.DB_DELETE)
    except Exception as e:
        await session.rollback()
        raise ResponseService.Error(biz_code=BizCode.ERR_INTERNAL, details={
                                    "message": "删除球队时发生未知错误"})
