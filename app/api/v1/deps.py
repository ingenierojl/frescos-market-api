from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.security import CurrentUser, decode_supabase_jwt
from app.db.session import get_db

DbSession = Annotated[AsyncSession, Depends(get_db)]

# auto_error=False para poder distinguir "no vino token" (invitado) de "token invalido"
_bearer_scheme = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(_bearer_scheme)],
) -> CurrentUser:
    """Requiere sesion. Usar en endpoints como /orders/me."""
    if credentials is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Falta el header Authorization")
    return decode_supabase_jwt(credentials.credentials)


async def get_current_user_optional(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(_bearer_scheme)],
) -> CurrentUser | None:
    """Permite invitado. Usar en endpoints como crear pedido sin login."""
    if credentials is None:
        return None
    return decode_supabase_jwt(credentials.credentials)


CurrentUserRequired = Annotated[CurrentUser, Depends(get_current_user)]
CurrentUserOptional = Annotated[CurrentUser | None, Depends(get_current_user_optional)]


def _email_matches(email: str | None, configured: str) -> bool:
    return bool(configured) and (email or "").strip().lower() == configured.strip().lower()


def is_admin_email(email: str | None) -> bool:
    return _email_matches(email, settings.admin_email)


def is_dispatcher_email(email: str | None) -> bool:
    return _email_matches(email, settings.dispatcher_email)


async def get_current_admin(current_user: CurrentUserRequired) -> CurrentUser:
    """Requiere sesion Y que el email coincida con ADMIN_EMAIL. Usar en /admin/*."""
    if not is_admin_email(current_user.email):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No autorizado")
    return current_user


async def get_current_dispatcher(current_user: CurrentUserRequired) -> CurrentUser:
    """Requiere sesion Y que el email coincida con DISPATCHER_EMAIL. Usar en /dispatcher/*."""
    if not is_dispatcher_email(current_user.email):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No autorizado")
    return current_user


async def get_current_team(current_user: CurrentUserRequired) -> CurrentUser:
    """Admin O despachador. Usar donde ambos deben poder actuar (ej: chat, cambiar estado)."""
    if not (is_admin_email(current_user.email) or is_dispatcher_email(current_user.email)):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No autorizado")
    return current_user


CurrentAdmin = Annotated[CurrentUser, Depends(get_current_admin)]
CurrentDispatcher = Annotated[CurrentUser, Depends(get_current_dispatcher)]
CurrentTeam = Annotated[CurrentUser, Depends(get_current_team)]
