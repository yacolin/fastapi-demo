from typing import Optional
from datetime import datetime

from pydantic import BaseModel, Field


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

