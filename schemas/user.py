from typing import Optional
from datetime import datetime

from pydantic import BaseModel, Field


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

