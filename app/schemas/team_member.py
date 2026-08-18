from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models.team_member import TeamRole


class TeamMemberCreate(BaseModel):
    email: str
    role: TeamRole


class TeamMemberUpdate(BaseModel):
    role: TeamRole


class TeamMemberOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: str
    role: TeamRole
    created_at: datetime
