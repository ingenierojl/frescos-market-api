from fastapi import APIRouter
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.api.v1.deps import DbSession
from app.models.product import Product
from app.schemas.product import ProductOut

router = APIRouter(prefix="/products", tags=["products"])


@router.api_route("", methods=["GET", "HEAD"], response_model=list[ProductOut])
async def list_products(db: DbSession, category: str | None = None):
    query = select(Product).where(Product.active.is_(True)).options(selectinload(Product.photos))
    if category:
        query = query.where(Product.category == category)
    result = await db.execute(query.order_by(Product.name))
    return result.scalars().all()
