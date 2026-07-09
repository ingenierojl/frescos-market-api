from fastapi import APIRouter
from sqlalchemy import select

from app.api.v1.deps import DbSession
from app.models.catalog_option import CatalogOption
from app.models.payment_option import PaymentOption
from app.schemas.catalog_option import CatalogOptionOut
from app.schemas.payment_option import PaymentOptionOut
from app.schemas.settings import PublicSettingsOut
from app.services.settings_service import get_or_create_settings

router = APIRouter(tags=["catalog"])


@router.get("/catalog-options", response_model=list[CatalogOptionOut])
async def list_catalog_options(db: DbSession, type: str | None = None):
    """Publico: opciones para los desplegables de unidad/categoria/departamento/ciudad."""
    query = select(CatalogOption)
    if type:
        query = query.where(CatalogOption.type == type)
    result = await db.execute(query.order_by(CatalogOption.sort_order, CatalogOption.id))
    return result.scalars().all()


@router.get("/settings", response_model=PublicSettingsOut)
async def get_public_settings(db: DbSession):
    """Publico: solo los datos de configuracion que el cliente necesita ver (ej. WhatsApp)."""
    return await get_or_create_settings(db)


@router.get("/payment-options", response_model=list[PaymentOptionOut])
async def list_payment_options(db: DbSession):
    """Publico: destinos de transferencia (Nequi, Daviplata, etc.) para mostrar al pagar."""
    result = await db.execute(select(PaymentOption).order_by(PaymentOption.sort_order, PaymentOption.id))
    return result.scalars().all()
