import jwt
from fastapi import HTTPException, status
from jwt import PyJWKClient

from app.core.config import settings

# Supabase publica sus claves publicas (ECC P-256 / ES256) en este endpoint.
# PyJWKClient las descarga y las cachea, y las refresca solas si cambia el "kid".
_jwks_client = PyJWKClient(settings.supabase_jwks_url)


class CurrentUser:
    def __init__(self, id: str, email: str | None, full_name: str | None = None):
        self.id = id
        self.email = email
        self.full_name = full_name


def decode_supabase_jwt(token: str) -> CurrentUser:
    """Valida el JWT que emite Supabase Auth tras el login (Google u otro proveedor).

    Supabase firma los tokens con una clave asimetrica (ES256), no con un secreto
    compartido: se verifica contra la clave publica que Supabase expone en su JWKS.
    """
    try:
        signing_key = _jwks_client.get_signing_key_from_jwt(token)
        payload = jwt.decode(
            token,
            signing_key.key,
            algorithms=["ES256"],
            audience="authenticated",
        )
    except jwt.PyJWTError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token invalido o expirado",
        ) from exc

    user_metadata = payload.get("user_metadata") or {}
    full_name = user_metadata.get("full_name") or user_metadata.get("name")
    return CurrentUser(id=payload["sub"], email=payload.get("email"), full_name=full_name)
