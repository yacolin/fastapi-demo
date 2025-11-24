from typing import Optional
import logging

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from datetime import datetime

from sqlalchemy import BigInteger, String, TIMESTAMP, text, select, func
from sqlalchemy.orm import declarative_base, Mapped, mapped_column
from sqlalchemy.ext.asyncio import AsyncSession

from utils import ResponseService
from utils.biz_code import BizCode
from configs.db import get_session
from sqlalchemy.exc import SQLAlchemyError

Base = declarative_base()
router = APIRouter(prefix="/products", tags=["products"])

# ORM model 对应你的表结构
class Product(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    category_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    price: Mapped[float] = mapped_column(nullable=False)
    stock: Mapped[int] = mapped_column(nullable=False)
    is_active: Mapped[bool] = mapped_column(nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP,
        server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"),
        nullable=False,
    )


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


# CRUD endpoints

@router.get("")
async def list_products(limit :int = 10, offset: int = 0, session: AsyncSession = Depends(get_session)):
    """
    List products with pagination.
    """
    try:
        if limit <= 0 or limit > 100:
            raise ResponseService.Error(biz_code=BizCode.INVALID_PAGE, details={"message": "Limit必须在1到100之间"})
        if offset < 0:
            raise ResponseService.Error(biz_code=BizCode.INVALID_PAGE, details={"message": "Offset必须为非负数"})

        # Get total count
        count_stmt = select(func.count()).select_from(Product)
        count_result = await session.execute(count_stmt)
        total = count_result.scalar()
        
        # Get paginated data
        stmt = select(Product).offset(offset).limit(limit)
        result = await session.execute(stmt)
        products = result.scalars().all()

        products_data = [ProductOut.from_orm(product).model_dump(mode="json") for product in products]
        return ResponseService.success(data={"items": products_data, "total": total})

    except ResponseService.Error:
        raise
    except SQLAlchemyError as e:
        await session.rollback()
        # 记录错误日志
        logging.exception("查询产品列表失败: %s", str(e))
        return ResponseService.internal_error("查询产品列表失败", BizCode.ERR_INTERNAL)
    except Exception as e:
        # 记录错误日志
        logging.exception("查询产品列表时发生未知错误: %s", str(e))
        raise ResponseService.Error(biz_code=BizCode.ERR_INTERNAL, details={"message": "查询产品列表时发生未知错误"})
    
      
@router.get("/{product_id}")
async def get_product(product_id: int, session: AsyncSession = Depends(get_session)):
    """
    Get a product by ID.
    """
    try:
        if product_id <= 0:
            return ResponseService.bad_request("Invalid product Id: 必须为正数")
        
        product = await session.get(Product, product_id)
        if not product:
            return ResponseService.not_found(f"产品ID {product_id} 不存在", BizCode.NOT_FOUND)
        
        product_dict = ProductOut.from_orm(product).model_dump(mode="json")
        return ResponseService.success(data=product_dict)

    except ResponseService.Error:
        raise
    except SQLAlchemyError as e:
        await session.rollback()
        # 记录错误日志
        logging.exception("查询产品失败: %s", str(e))
        return ResponseService.internal_error("查询产品失败", BizCode.ERR_INTERNAL)
    except Exception as e:
        # 记录错误日志
        logging.exception("查询产品时发生未知错误: %s", str(e))
        raise ResponseService.Error(biz_code=BizCode.ERR_INTERNAL, details={"message": "查询产品时发生未知错误"})


    

@router.put("/{product_id}")
async def update_product(product_id: int, payload: ProductUpdate, session: AsyncSession = Depends(get_session)):
    """
    Update a product by ID.
    """
    try:
        if product_id <= 0:
            return ResponseService.bad_request("Invalid product Id: 必须为正数")
            
        product = await session.get(Product, product_id)
        if not product:
            return ResponseService.not_found(f"产品ID {product_id} 不存在", BizCode.NOT_FOUND)

        # Check if at least one field is provided
        if not payload.model_dump(exclude_unset=True):
            return ResponseService.bad_request("至少需要提供一个字段进行更新")
        
        # Update the product with the provided payload (using the payload model)
        for key, value in payload.model_dump(exclude_unset=True).items():
            setattr(product, key, value)

        session.add(product)
        await session.commit()
        await session.refresh(product)

        product_data = ProductOut.from_orm(product).model_dump(mode="json")
        return ResponseService.success(data=product_data)

    except ResponseService.Error:
        raise
    except SQLAlchemyError as e:
        await session.rollback()
        # 记录错误日志
        logging.exception("更新产品失败: %s", str(e))
        return ResponseService.internal_error("更新产品失败", BizCode.ERR_INTERNAL)
    except Exception as e:
        # 记录错误日志
        logging.exception("更新产品时发生未知错误: %s", str(e))
        raise ResponseService.Error(biz_code=BizCode.ERR_INTERNAL, details={"message": "更新产品时发生未知错误"})

@router.delete("/{product_id}")
async def delete_product(product_id: int, session: AsyncSession = Depends(get_session)):
    """
    Delete a product by ID.
    """
    try:
        if product_id <= 0:
            return ResponseService.bad_request("Invalid product Id: 必须为正数")
            
        product = await session.get(Product, product_id)
        if not product:
            return ResponseService.not_found(f"产品ID {product_id} 不存在", BizCode.NOT_FOUND)

        await session.delete(product)
        await session.commit()

        return ResponseService.deleted()

    except ResponseService.Error:
        raise
    except SQLAlchemyError as e:
        await session.rollback()
        # 记录错误日志
        logging.exception("删除产品失败: %s", str(e))
        return ResponseService.internal_error("删除产品失败", BizCode.DB_DELETE)
    except Exception as e:
        # 记录错误日志
        logging.exception("删除产品时发生未知错误: %s", str(e))
        raise ResponseService.Error(biz_code=BizCode.ERR_INTERNAL, details={"message": "删除产品时发生未知错误"})
