from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import CurrentUser, decode_supabase_jwt
from app.db.session import get_db
from app.models.team_member import TeamMember, TeamRole

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


async def _has_role(db: AsyncSession, email: str | None, role: TeamRole) -> bool:
    if not email:
        return False
    result = await db.execute(
        select(TeamMember).where(TeamMember.email == email.strip().lower(), TeamMember.role == role.value)
    )
    return result.scalar_one_or_none() is not None


async def is_admin_email(email: str | None, db: AsyncSession) -> bool:
    return await _has_role(db, email, TeamRole.admin)


async def is_dispatcher_email(email: str | None, db: AsyncSession) -> bool:
    return await _has_role(db, email, TeamRole.dispatcher)


async def get_current_admin(current_user: CurrentUserRequired, db: DbSession) -> CurrentUser:
    """Requiere sesion Y ser admin en team_members. Usar en /admin/*."""
    if not await is_admin_email(current_user.email, db):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No autorizado")
    return current_user


async def get_current_dispatcher(current_user: CurrentUserRequired, db: DbSession) -> CurrentUser:
    """Requiere sesion Y ser despachador en team_members."""
    if not await is_dispatcher_email(current_user.email, db):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No autorizado")
    return current_user


async def get_current_team(current_user: CurrentUserRequired, db: DbSession) -> CurrentUser:
    """Admin O despachador. Usar donde ambos deben poder actuar (ej: chat, cambiar estado)."""
    if not (await is_admin_email(current_user.email, db) or await is_dispatcher_email(current_user.email, db)):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No autorizado")
    return current_user


CurrentAdmin = Annotated[CurrentUser, Depends(get_current_admin)]
CurrentDispatcher = Annotated[CurrentUser, Depends(get_current_dispatcher)]
CurrentTeam = Annotated[CurrentUser, Depends(get_current_team)]
