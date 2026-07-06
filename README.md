# Frescos Market API

Backend en FastAPI para [frescos-market](https://github.com/ingenierojl/frescos-market). Postgres en Supabase, autenticación con Google vía Supabase Auth (este backend solo valida el JWT que emite Supabase, no maneja OAuth directamente).

## Estructura

```
app/
  main.py               # instancia FastAPI, CORS, monta routers
  core/
    config.py           # settings (pydantic-settings, lee .env)
    security.py          # valida el JWT de Supabase
  db/
    base.py              # Base declarativa de SQLAlchemy
    session.py           # engine async + get_db()
  models/                # Product, Order, OrderItem (SQLAlchemy)
  schemas/               # Pydantic (request/response)
  api/v1/
    deps.py              # DbSession, CurrentUserRequired, CurrentUserOptional
    routes/
      products.py        # GET /api/v1/products
      orders.py          # POST /api/v1/orders, GET /api/v1/orders/me
      users.py           # GET /api/v1/users/me
  services/
    order_service.py     # lógica de creación de pedido (valida stock, calcula total)
alembic/                 # migraciones
```

## Setup local

```bash
python -m venv .venv
.venv/Scripts/activate       # Windows
pip install -r requirements.txt
cp .env.example .env          # y completar con tus datos reales de Supabase
```

Variables en `.env` (ver `.env.example`):
- `DATABASE_URL`: connection string de Supabase, con el prefijo `postgresql+asyncpg://` (Supabase te da `postgresql://`, hay que cambiar el prefijo a mano).
- `SUPABASE_JWT_SECRET`: Settings → API → JWT Secret, en el dashboard de Supabase.
- `CORS_ORIGINS`: dominios del frontend separados por coma.

## Primera migración

Con `.env` completo y apuntando a tu Supabase real:

```bash
alembic revision --autogenerate -m "init: products, orders, order_items"
alembic upgrade head
```

Esto crea las tablas `products`, `orders`, `order_items` en tu Postgres de Supabase.

## Correr local

```bash
uvicorn app.main:app --reload
```

Docs interactivas en `http://localhost:8000/docs`.

## Deploy en Render

- **Language**: Python 3
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- Variables de entorno (`DATABASE_URL`, `SUPABASE_JWT_SECRET`, `CORS_ORIGINS`) configuradas en Render → Environment, no committeadas al repo.

## Endpoints actuales

| Método | Ruta | Auth | Qué hace |
|---|---|---|---|
| GET | `/health` | no | healthcheck para Render |
| GET | `/api/v1/products` | no | lista productos activos (`?category=hortalizas\|frutas`) |
| POST | `/api/v1/orders` | opcional | crea un pedido (con o sin sesión — invitado permitido) |
| GET | `/api/v1/orders/me` | requerida | historial de pedidos del usuario logueado |
| GET | `/api/v1/users/me` | requerida | id/email del usuario actual (del JWT) |

## Pendiente / próximos pasos

- Endpoint admin para crear/editar productos (por ahora se insertan a mano en la tabla `products`, o vía un script de seed).
- Semilla inicial: migrar el array `PRODUCTS` de `frescos-market/script.js` a filas reales en la tabla `products`.
- El frontend estático debe cambiar de usar el array hardcodeado a consumir `GET /api/v1/products`, y el checkout debe llamar `POST /api/v1/orders` además de (o en vez de) armar el link de WhatsApp.
- Rol admin / panel simple.
- Pagos en línea (fuera de alcance por ahora).
