from typing import Union

from fastapi import APIRouter

from utils import ResponseService
from utils.biz_code import BizCode
from schemas.item import Item
from services import item as item_service

router = APIRouter(prefix="/items", tags=["items"])


@router.get("/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    """Get an item by ID"""
    try:
        if item_id <= 0:
            return ResponseService.bad_request("Invalid item_id: 必须为正数")

        item_data = item_service.get_item(item_id, q)
        return ResponseService.success(data=item_data)
    except ResponseService.Error:
        raise
    except Exception as e:
        raise ResponseService.Error(biz_code=BizCode.ERR_INTERNAL, details={
                                    "message": "查询商品时发生未知错误"})


@router.put("/{item_id}")
def update_item(item_id: int, item: Item):
    """Update an item by ID"""
    try:
        if item_id <= 0:
            return ResponseService.bad_request("Invalid item_id: 必须为正数")

        updated_data = item_service.update_item(item_id, item)
        return ResponseService.updated(data=updated_data)
    except ResponseService.Error:
        raise
    except Exception as e:
        raise ResponseService.Error(biz_code=BizCode.ERR_INTERNAL, details={
                                    "message": "更新商品时发生未知错误"})
