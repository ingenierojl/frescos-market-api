from sqlalchemy.ext.asyncio import AsyncSession

from app.models.settings import AppSettings

SETTINGS_ID = 1


async def get_or_create_settings(db: AsyncSession) -> AppSettings:
    """Fila unica de configuracion (id=1), creada la primera vez que se necesita."""
    settings_row = await db.get(AppSettings, SETTINGS_ID)
    if settings_row is None:
        settings_row = AppSettings(id=SETTINGS_ID)
        db.add(settings_row)
        await db.commit()
        await db.refresh(settings_row)
    return settings_row
