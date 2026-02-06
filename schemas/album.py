from typing import Optional
from datetime import datetime

from pydantic import BaseModel, Field, field_validator


class AlbumBase(BaseModel):
    name: Optional[str] = None
    author: Optional[str] = None
    description: Optional[str] = None
    liked: Optional[int] = Field(default=0, ge=0)


class AlbumCreate(AlbumBase):
    name: str = Field(..., min_length=1, max_length=255)
    author: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    liked: int = Field(default=0, ge=0, le=1000000)

    @field_validator("name", mode="before")
    def name_strip_nonempty(cls, v):
        if v is None:
            raise ValueError("name 不能为空或全为空格")
        v = v.strip()
        if not v:
            raise ValueError("name 不能为空或全为空格")
        return v

    @field_validator("author", "description", mode="before")
    def strip_optional_str(cls, v: Optional[str]):
        if v is None:
            return v
        v = v.strip()
        return v or None


class AlbumUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    author: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    liked: Optional[int] = Field(default=None, ge=0, le=1000000)

    @field_validator("name", mode="before")
    def name_strip_nonempty(cls, v: Optional[str]):
        if v is None:
            return v
        v = v.strip()
        if not v:
            raise ValueError("name 不能为空或全为空格")
        return v

    @field_validator("author", "description", mode="before")
    def strip_optional_str(cls, v: Optional[str]):
        if v is None:
            return v
        v = v.strip()
        return v or None


class AlbumOut(AlbumBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: int(v.timestamp()) if v else None
        }

