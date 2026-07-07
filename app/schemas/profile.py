from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ProfileUpsert(BaseModel):
    phone: str
    address: str
    department: str
    city: str


class ProfileOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    phone: str
    address: str
    department: str
    city: str
    updated_at: datetime
