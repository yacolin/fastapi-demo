from typing import Optional, Tuple, List

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from models.product import Product
from schemas.product import ProductCreate, ProductUpdate


async def create_product(session: AsyncSession, payload: ProductCreate) -> Product:
    """
    Create a new product and persist it to the database.
    """
    product = Product(
        name=payload.name,
        category_id=payload.category_id,
        price=payload.price,
        stock=payload.stock,
        is_active=payload.is_active,
    )
    session.add(product)
    await session.commit()
    await session.refresh(product)
    return product


async def list_products(session: AsyncSession, limit: int, offset: int) -> Tuple[List[Product], int]:
    """
    List products with pagination.
    """
    # Get total count
    count_stmt = select(func.count()).select_from(Product)
    count_result = await session.execute(count_stmt)
    total = count_result.scalar() or 0

    stmt = select(Product).offset(offset).limit(limit)
    result = await session.execute(stmt)
    products = result.scalars().all()
    return products, total


async def get_product_by_id(session: AsyncSession, product_id: int) -> Optional[Product]:
    """
    Get a product by ID.
    """
    return await session.get(Product, product_id)


async def update_product(session: AsyncSession, product: Product, payload: ProductUpdate) -> Product:
    """
    Update a product.
    """
    if payload.name is not None:
        product.name = payload.name
    if payload.category_id is not None:
        product.category_id = payload.category_id
    if payload.price is not None:
        product.price = payload.price
    if payload.stock is not None:
        product.stock = payload.stock
    if payload.is_active is not None:
        product.is_active = payload.is_active

    session.add(product)
    await session.commit()
    await session.refresh(product)
    return product


async def delete_product(session: AsyncSession, product: Product) -> None:
    """
    Delete a product.
    """
    await session.delete(product)
    await session.commit()
