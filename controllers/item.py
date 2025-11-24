from typing import Union

from fastapi import APIRouter
from pydantic import BaseModel

from utils import ResponseService
from utils.biz_code import BizCode

router = APIRouter(prefix="/items", tags=["items"])

class Item(BaseModel):
    name: str
    price: float
    is_offer: Union[bool, None] = None


@router.get("/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    """Get an item by ID"""
    try:
        if item_id <= 0:
            return ResponseService.bad_request("Invalid item_id: 必须为正数")
        
        # Mock data - in real scenario, this would query from database
        item_data = {"item_id": item_id, "q": q}
        return ResponseService.success(data=item_data)
    except ResponseService.Error:
        raise
    except Exception as e:
        raise ResponseService.Error(biz_code=BizCode.ERR_INTERNAL, details={"message": "查询商品时发生未知错误"})


@router.put("/{item_id}")
def update_item(item_id: int, item: Item):
    """Update an item by ID"""
    try:
        if item_id <= 0:
            return ResponseService.bad_request("Invalid item_id: 必须为正数")
        
        # Mock update - in real scenario, this would update in database
        updated_data = {"item_name": item.name, "item_id": item_id, "price": item.price, "is_offer": item.is_offer}
        return ResponseService.updated(data=updated_data)
    except ResponseService.Error:
        raise
    except Exception as e:
        raise ResponseService.Error(biz_code=BizCode.ERR_INTERNAL, details={"message": "更新商品时发生未知错误"})
