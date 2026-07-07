"""
Siembra la tabla products con el catalogo actual del frontend
(frescos-market/script.js -- PRODUCTS). Correr una sola vez (o cuando
el catalogo cambie) con:

    python scripts/seed_products.py

Requiere DATABASE_URL en el .env local apuntando al Supabase real.
Es idempotente: si un slug ya existe, actualiza sus datos en vez de
duplicarlo.
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlalchemy import select

from app.db.session import AsyncSessionLocal
from app.models.product import Product

PRODUCTS = [
    {"slug": "papa", "name": "Papa", "unit": "por libra", "price": 1900, "category": "hortalizas", "photo_url": "assets/products/camote.jpg"},
    {"slug": "tomate", "name": "Tomate", "unit": "por libra", "price": 2200, "category": "hortalizas", "photo_url": "assets/products/tomate.jpg"},
    {"slug": "cebolla", "name": "Cebolla", "unit": "por libra", "price": 2000, "category": "hortalizas", "photo_url": "assets/products/cebolla.jpg"},
    {"slug": "zanahoria", "name": "Zanahoria", "unit": "por libra", "price": 1700, "category": "hortalizas", "photo_url": "assets/products/zanahoria.jpg"},
    {"slug": "pimenton", "name": "Pimentón", "unit": "por libra", "price": 2600, "category": "hortalizas", "photo_url": "assets/products/pimenton.jpg"},
    {"slug": "cilantro", "name": "Cilantro", "unit": "atado", "price": 1500, "category": "hortalizas", "photo_url": "assets/products/cilantro.jpg"},
    {"slug": "aguacate", "name": "Aguacate", "unit": "por unidad", "price": 2500, "category": "frutas", "photo_url": "assets/products/aguacate.jpg"},
    {"slug": "manzana", "name": "Manzana", "unit": "por libra", "price": 3200, "category": "frutas", "photo_url": "assets/products/manzana.jpg"},
    {"slug": "banano", "name": "Banano", "unit": "por libra", "price": 1500, "category": "frutas", "photo_url": "assets/products/banano.jpg"},
    {"slug": "naranja", "name": "Naranja", "unit": "por libra", "price": 1900, "category": "frutas", "photo_url": "assets/products/naranja.jpg"},
    {"slug": "mango", "name": "Mango", "unit": "por unidad", "price": 2300, "category": "frutas", "photo_url": "assets/products/mango.jpg"},
    {"slug": "fresa", "name": "Fresa", "unit": "canasta", "price": 5500, "category": "frutas", "photo_url": "assets/products/fresa.jpg"},
]


async def seed():
    async with AsyncSessionLocal() as db:
        for data in PRODUCTS:
            result = await db.execute(select(Product).where(Product.slug == data["slug"]))
            existing = result.scalar_one_or_none()
            if existing:
                for key, value in data.items():
                    setattr(existing, key, value)
                print(f"actualizado: {data['slug']}")
            else:
                db.add(Product(**data))
                print(f"creado: {data['slug']}")
        await db.commit()


if __name__ == "__main__":
    asyncio.run(seed())
