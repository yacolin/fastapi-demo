import logging

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from utils import ResponseService
from utils.biz_code import BizCode
from configs.db import get_session
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from schemas.product import ProductCreate, ProductOut, ProductUpdate
from services import product as product_service

router = APIRouter(prefix="/products", tags=["products"])


# CRUD endpoints

@router.post("")
async def create_product(payload: ProductCreate, session: AsyncSession = Depends(get_session)):
    """
    Create a new product.
    """
    try:
        product = await product_service.create_product(session=session, payload=payload)
        product_data = ProductOut.model_validate(product).model_dump(mode="json")
        return ResponseService.created(data=product_data)

    except IntegrityError as e:
        await session.rollback()
        return ResponseService.db_error("数据完整性错误", BizCode.DB_CREATE)
    except SQLAlchemyError as e:
        await session.rollback()
        logging.exception("创建产品失败: %s", str(e))
        return ResponseService.db_error("创建产品失败", BizCode.DB_CREATE)
    except Exception as e:
        await session.rollback()
        logging.exception("创建产品时发生未知错误: %s", str(e))
        raise ResponseService.Error(biz_code=BizCode.ERR_INTERNAL, details={"message": "创建产品时发生未知错误"})

    
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
        products, total = await product_service.list_products(
            session=session, 
            limit=limit, 
            offset=offset
        )

        products_data = [ProductOut.model_validate(product).model_dump(mode="json") for product in products]
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

        product = await product_service.get_product_by_id(session=session, product_id=product_id)
        if not product:
            return ResponseService.not_found(f"产品ID {product_id} 不存在", BizCode.NOT_FOUND)
        
        product_dict = ProductOut.model_validate(product).model_dump(mode="json")
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

        product = await product_service.get_product_by_id(session=session, product_id=product_id)
        if not product:
            return ResponseService.not_found(f"产品ID {product_id} 不存在", BizCode.NOT_FOUND)

        # Check if at least one field is provided
        if not payload.model_dump(exclude_unset=True):
            return ResponseService.bad_request("至少需要提供一个字段进行更新")
        
        product = await product_service.update_product(session=session, product=product, payload=payload)

        product_data = ProductOut.model_validate(product).model_dump(mode="json")
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

        product = await product_service.get_product_by_id(session=session, product_id=product_id)
        if not product:
            return ResponseService.not_found(f"产品ID {product_id} 不存在", BizCode.NOT_FOUND)

        await product_service.delete_product(session=session, product=product)
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
