from typing import Union

from schemas.item import Item


def get_item(item_id: int, q: Union[str, None] = None) -> dict:
    """
    Get an item by ID with optional query parameter.
    """
    return {"item_id": item_id, "q": q}


def update_item(item_id: int, item: Item) -> dict:
    """
    Update an item by ID.
    """
    return {"item_name": item.name, "item_id": item_id, "price": item.price, "is_offer": item.is_offer}
