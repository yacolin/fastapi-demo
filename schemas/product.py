from typing import Optional
from datetime import datetime

from pydantic import BaseModel, Field


# Pydantic schemas
class ProductBase(BaseModel):
    name: Optional[str] = Field(None, description="Product name")
    category_id: Optional[int] = Field(None, description="Product category ID")
    price: Optional[float] = Field(None, description="Product price")
    stock: Optional[int] = Field(None, description="Product stock")
    is_active: Optional[bool] = Field(None, description="Product active status")

class ProductCreate(ProductBase):
    pass


class ProductUpdate(ProductBase):
    pass


class ProductOut(ProductBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: int(v.timestamp()) if v else None
        }

