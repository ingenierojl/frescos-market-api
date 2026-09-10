"""
Snapshot de la tabla products tal como esta en produccion (verificado
contra la base real el 10-sep-2026, ver backups/backup-20260910-120129.json).
El catalogo real ya no vive aqui ni en script.js -- ambos leen de
GET /products -- esto es solo un respaldo/semilla para reconstruir la
tabla desde cero si hiciera falta. Correr con:

    python scripts/seed_products.py

Requiere DATABASE_URL en el .env local apuntando al Supabase real.
Es idempotente: si un slug ya existe, actualiza sus datos en vez de
duplicarlo -- por eso, si vas a correrlo, confirma antes que estos
precios siguen siendo los reales (pueden haber cambiado desde el panel
admin sin que este archivo se actualice solo).
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlalchemy import select

from app.db.session import AsyncSessionLocal
from app.models.product import Product

PRODUCTS = [
    {"slug": "papa", "name": "Papa", "unit": "por libra", "price": 1900, "category": "hortalizas", "photo_url": "https://ezpqfzjbauxluvxmqxvj.supabase.co/storage/v1/object/public/product-photos/1783640954512-jvfwz251uhb.jpg"},
    {"slug": "tomate", "name": "Tomate", "unit": "por libra", "price": 3000, "category": "hortalizas", "photo_url": "https://ezpqfzjbauxluvxmqxvj.supabase.co/storage/v1/object/public/product-photos/tomate-1783699549673191300.jpg"},
    {"slug": "cebolla", "name": "Cebolla", "unit": "por libra", "price": 2000, "category": "hortalizas", "photo_url": "https://ezpqfzjbauxluvxmqxvj.supabase.co/storage/v1/object/public/product-photos/1783642455966-01vsyp02tcwv.jpg"},
    {"slug": "zanahoria", "name": "Zanahoria", "unit": "por libra", "price": 2500, "category": "hortalizas", "photo_url": "https://ezpqfzjbauxluvxmqxvj.supabase.co/storage/v1/object/public/product-photos/1783642253208-xn63ns5lerq.jpg"},
    {"slug": "pimenton", "name": "Pimentón", "unit": "por libra", "price": 3000, "category": "hortalizas", "photo_url": "https://ezpqfzjbauxluvxmqxvj.supabase.co/storage/v1/object/public/product-photos/1783643037086-n5wsdbh1mdi.jpg"},
    {"slug": "cilantro", "name": "Cilantro", "unit": "atado", "price": 2000, "category": "hortalizas", "photo_url": "https://ezpqfzjbauxluvxmqxvj.supabase.co/storage/v1/object/public/product-photos/cilantro-1783699549114138900.jpg"},
    {"slug": "aguacate", "name": "Aguacate", "unit": "por libra", "price": 1500, "category": "frutas", "photo_url": "https://ezpqfzjbauxluvxmqxvj.supabase.co/storage/v1/object/public/product-photos/aguacate-1783699547492218400.jpg"},
    {"slug": "manzana", "name": "Manzana Roja", "unit": "por unidad", "price": 1200, "category": "frutas", "photo_url": "https://ezpqfzjbauxluvxmqxvj.supabase.co/storage/v1/object/public/product-photos/1783641087407-yraeeejbmdq.jpg"},
    {"slug": "Manzana Verde", "name": "Manzana Verde", "unit": "por unidad", "price": 1400, "category": "frutas", "photo_url": "https://ezpqfzjbauxluvxmqxvj.supabase.co/storage/v1/object/public/product-photos/1783642009256-3jbvis6jd5l.jpg"},
    {"slug": "banano", "name": "Banano", "unit": "por kilo", "price": 3000, "category": "frutas", "photo_url": "https://ezpqfzjbauxluvxmqxvj.supabase.co/storage/v1/object/public/product-photos/banano-1783699548519677100.jpg"},
    {"slug": "naranja", "name": "Naranja", "unit": "por libra", "price": 1400, "category": "frutas", "photo_url": "https://ezpqfzjbauxluvxmqxvj.supabase.co/storage/v1/object/public/product-photos/naranja-1783699549414044400.jpg"},
    {"slug": "mango", "name": "Mango", "unit": "por libra", "price": 8000, "category": "frutas", "photo_url": "https://ezpqfzjbauxluvxmqxvj.supabase.co/storage/v1/object/public/product-photos/1783642939414-bi0f6dy86jn.jpg"},
    {"slug": "fresa", "name": "Fresa", "unit": "por libra", "price": 5000, "category": "frutas", "photo_url": "https://ezpqfzjbauxluvxmqxvj.supabase.co/storage/v1/object/public/product-photos/1783642840166-bds1b205zxk.jpg"},
    {"slug": "arandanos", "name": "Arándanos", "unit": "por libra", "price": 9000, "category": "frutas", "photo_url": "https://ezpqfzjbauxluvxmqxvj.supabase.co/storage/v1/object/public/product-photos/1783642720958-3rw4gpyy6mg.jpg"},
    {"slug": "7777778", "name": "Licuadora con Picatodo", "unit": "por unidad", "price": 150000, "category": "Hogar", "photo_url": "https://ezpqfzjbauxluvxmqxvj.supabase.co/storage/v1/object/public/product-photos/1783694282971-yyvri5fy42f.jpg"},
    {"slug": "7777777", "name": "Estante, Repisa para baño", "unit": "por unidad", "price": 95000, "category": "Hogar", "photo_url": "https://ezpqfzjbauxluvxmqxvj.supabase.co/storage/v1/object/public/product-photos/1783695452321-e3hnn8ap4vj.jpg", "stock": 0},
    {"slug": "pina-golden", "name": "Piña Golden", "unit": "por unidad", "price": 4500, "category": "frutas", "photo_url": "assets/products/pina-golden.jpg"},
    {"slug": "papaya", "name": "Papaya", "unit": "por unidad", "price": 3500, "category": "frutas", "photo_url": "assets/products/papaya.jpg"},
    {"slug": "platano-verde", "name": "Plátano Verde", "unit": "por unidad", "price": 800, "category": "frutas", "photo_url": "assets/products/platano-verde.jpg"},
    {"slug": "arveja", "name": "Arveja en Cáscara", "unit": "por libra", "price": 3000, "category": "hortalizas", "photo_url": "assets/products/arveja.jpg"},
    {"slug": "yuca", "name": "Yuca", "unit": "por libra", "price": 1800, "category": "hortalizas", "photo_url": "assets/products/yuca.jpg"},
    {"slug": "papa-criolla", "name": "Papa Criolla", "unit": "por libra", "price": 2800, "category": "hortalizas", "photo_url": "assets/products/papa-criolla.jpg"},
    {"slug": "lechuga-crespa", "name": "Lechuga Crespa", "unit": "por unidad", "price": 2000, "category": "hortalizas", "photo_url": "assets/products/lechuga-crespa.jpg"},
    {"slug": "coliflor", "name": "Coliflor", "unit": "por unidad", "price": 3500, "category": "hortalizas", "photo_url": "assets/products/coliflor.jpg"},
    {"slug": "espinaca", "name": "Espinaca", "unit": "por unidad", "price": 2000, "category": "hortalizas", "photo_url": "assets/products/espinaca.jpg"},
    {"slug": "cebolla-larga", "name": "Cebolla Larga", "unit": "atado", "price": 1500, "category": "hortalizas", "photo_url": "assets/products/cebolla-larga.jpg"},
    {"slug": "cebolla-cabezona", "name": "Cebolla Cabezona", "unit": "por libra", "price": 2000, "category": "hortalizas", "photo_url": "assets/products/cebolla-cabezona.jpg"},
    {"slug": "ahuyama", "name": "Ahuyama Mantequilla", "unit": "por libra", "price": 1800, "category": "hortalizas", "photo_url": "assets/products/ahuyama.jpg"},
    {"slug": "brocoli", "name": "Brócoli", "unit": "por unidad", "price": 3500, "category": "hortalizas", "photo_url": "assets/products/brocoli.jpg"},
    {"slug": "pepino", "name": "Pepino", "unit": "por unidad", "price": 1200, "category": "hortalizas", "photo_url": "assets/products/pepino.jpg"},
    {"slug": "patilla-baby", "name": "Patilla Baby", "unit": "por unidad", "price": 6000, "category": "frutas", "photo_url": "assets/products/patilla-baby.jpg"},
    {"slug": "guanabana", "name": "Guanábana", "unit": "por unidad", "price": 5000, "category": "frutas", "photo_url": "assets/products/guanabana.jpg"},
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
