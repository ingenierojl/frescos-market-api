"""Respaldo manual: vuelca todas las tablas de la base real a un JSON local.

No se commitea (queda fuera del repo, en una carpeta local aparte) -- es solo
una red de seguridad antes de cambios estructurales grandes (ej. reescribir
policies de RLS). Uso: python scripts/backup_db.py
"""
import asyncio
import json
import sys
from datetime import datetime, date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

from app.core.config import settings

TABLES = [
    "orders",
    "order_items",
    "order_messages",
    "products",
    "product_photos",
    "catalog_options",
    "payment_options",
    "app_settings",
    "profiles",
    "alembic_version",
]


def _json_default(value):
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    return str(value)


async def main():
    engine = create_async_engine(settings.database_url)
    dump = {}

    async with engine.connect() as conn:
        for table in TABLES:
            result = await conn.execute(text(f"SELECT * FROM {table}"))
            rows = [dict(row._mapping) for row in result]
            dump[table] = rows
            print(f"{table}: {len(rows)} filas")

    await engine.dispose()

    out_dir = Path(__file__).parent.parent / "backups"
    out_dir.mkdir(exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    out_file = out_dir / f"backup-{stamp}.json"
    out_file.write_text(json.dumps(dump, default=_json_default, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\nRespaldo guardado en: {out_file}")


if __name__ == "__main__":
    asyncio.run(main())
