from typing import Optional
from datetime import datetime

from pydantic import BaseModel, Field


class SongBase(BaseModel):
    album_id: int = Field(..., description="Album ID (foreign key)")
    title: str = Field(..., min_length=1, max_length=255, description="Song title")
    duration: Optional[int] = Field(default=None, ge=0, description="Duration in seconds")
    track_number: Optional[int] = Field(default=None, ge=1, description="Track number in album")


class SongCreate(SongBase):
    pass


class SongUpdate(BaseModel):
    album_id: Optional[int] = Field(default=None, description="Album ID (foreign key)")
    title: Optional[str] = Field(default=None, min_length=1, max_length=255, description="Song title")
    duration: Optional[int] = Field(default=None, ge=0, description="Duration in seconds")
    track_number: Optional[int] = Field(default=None, ge=1, description="Track number in album")


class SongOut(BaseModel):
    id: int
    album_id: int
    title: str
    duration: Optional[int]
    track_number: Optional[int]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: int(v.timestamp()) if v else None
        }

