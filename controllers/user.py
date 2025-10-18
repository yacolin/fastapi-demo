"""
User Authentication Module
User registration, login, and token refresh endpoints
"""
from typing import Optional

from fastapi import APIRouter, Depends, status
from pydantic import BaseModel, Field
from datetime import datetime

from sqlalchemy import Integer, String, TIMESTAMP, text, select
from sqlalchemy.orm import declarative_base, Mapped, mapped_column
from sqlalchemy.ext.asyncio import AsyncSession

from utils import AuthService, ResponseService
from utils.biz_code import (
    INVALID_PWD, USER_NOT_FOUND, DB_CREATE,
    ACCESS_TK_GEN, TK_INVALID, TK_USER_ID, ERR_INTERNAL
)
from middlewares.jwt_middleware import get_current_user
from configs import get_session
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

Base = declarative_base()
router = APIRouter(prefix="/users", tags=["users"])


# ORM model for users table
class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    password: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"), nullable=False)
    updated_at: Mapped[Optional[datetime]] = mapped_column(
        TIMESTAMP,
        server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"),
        nullable=True,
    )


# Pydantic schemas
class LoginInput(BaseModel):
    username: str = Field(..., min_length=3, max_length=255, description="Username")
    password: str = Field(..., min_length=6, max_length=255, description="Password")


class RegisterInput(BaseModel):
    username: str = Field(..., min_length=3, max_length=255, description="Username")
    password: str = Field(..., min_length=6, max_length=255, description="Password")


class RefreshInput(BaseModel):
    refresh_token: str = Field(..., description="Refresh token")


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str


class AccessTokenResponse(BaseModel):
    access_token: str


class UserOut(BaseModel):
    id: int
    username: str
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: int(v.timestamp()) if v else None
        }


# Authentication endpoints

@router.post("/login", status_code=status.HTTP_200_OK)
async def login(payload: LoginInput, session: AsyncSession = Depends(get_session)):
    """User login endpoint - Returns access_token and refresh_token"""
    try:
        # Find user by username
        stmt = select(User).where(User.username == payload.username)
        result = await session.execute(stmt)
        user = result.scalar_one_or_none()
        
        if not user:
            return ResponseService.unauthorized("用户不存在", USER_NOT_FOUND)
        
        # Verify password
        if not AuthService.verify_password(payload.password, user.password):
            return ResponseService.unauthorized("密码错误", INVALID_PWD)
        
        # Generate token pair
        try:
            tokens = AuthService.create_token_pair(user.id)
            return ResponseService.success(data=tokens)
        except Exception as e:
            return ResponseService.internal_error("生成token失败", ACCESS_TK_GEN)
        
    except SQLAlchemyError as e:
        import traceback
        traceback.print_exc()
        return ResponseService.internal_error("登录时发生数据库错误", ERR_INTERNAL)
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise ResponseService.Error(biz_code=ERR_INTERNAL, details={"message": "登录时发生未知错误"})


@router.post("/register", status_code=status.HTTP_200_OK)
async def register(payload: RegisterInput, session: AsyncSession = Depends(get_session)):
    """User registration endpoint"""
    try:
        # Check if user already exists
        stmt = select(User).where(User.username == payload.username)
        result = await session.execute(stmt)
        existing_user = result.scalar_one_or_none()
        
        if existing_user:
            return ResponseService.bad_request("用户名已存在")
        
        # Hash password
        try:
            hashed_password = AuthService.hash_password(payload.password)
        except Exception as e:
            return ResponseService.internal_error("密码加密失败", DB_CREATE)
        
        # Create new user
        user = User(
            username=payload.username,
            password=hashed_password,
        )
        
        session.add(user)
        await session.commit()
        await session.refresh(user)
        
        return ResponseService.success()
        
    except IntegrityError as e:
        await session.rollback()
        return ResponseService.bad_request("用户名已存在")
    except SQLAlchemyError as e:
        await session.rollback()
        import traceback
        traceback.print_exc()
        return ResponseService.internal_error("注册失败", DB_CREATE)
    except Exception as e:
        await session.rollback()
        import traceback
        traceback.print_exc()
        raise ResponseService.Error(biz_code=ERR_INTERNAL, details={"message": "注册时发生未知错误"})


@router.post("/refresh", status_code=status.HTTP_200_OK)
async def refresh(payload: RefreshInput, session: AsyncSession = Depends(get_session)):
    """Refresh access token using refresh token"""
    try:
        # Validate refresh token
        claims = AuthService.validate_token(payload.refresh_token)
        
        if not claims:
            return ResponseService.unauthorized("无效的refresh token", TK_INVALID)
        
        # Extract user_id from claims
        user_id = claims.get("user_id")
        if not user_id:
            return ResponseService.unauthorized("refresh token缺少user_id", TK_USER_ID)
        
        # Verify user still exists
        user = await session.get(User, user_id)
        if not user:
            return ResponseService.unauthorized("用户不存在", USER_NOT_FOUND)
        
        # Generate new access token
        try:
            new_access_token = AuthService.create_access_token(user_id)
            return ResponseService.success(data={"access_token": new_access_token})
        except Exception as e:
            return ResponseService.internal_error("生成新的access token失败", ACCESS_TK_GEN)
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise ResponseService.Error(biz_code=ERR_INTERNAL, details={"message": "刷新token时发生未知错误"})


@router.get("/me", status_code=status.HTTP_200_OK)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Get current authenticated user information - Requires JWT authentication"""
    try:
        user_data = UserOut.from_orm(current_user).model_dump(mode='json')
        return ResponseService.success(data=user_data)
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise ResponseService.Error(biz_code=ERR_INTERNAL, details={"message": "获取用户信息时发生未知错误"})
