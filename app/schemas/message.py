import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, model_validator


class MessageCreate(BaseModel):
    body: str | None = Field(default=None, max_length=1000)
    image_url: str | None = Field(default=None, max_length=300)

    @model_validator(mode="after")
    def require_body_or_image(self) -> "MessageCreate":
        if not (self.body and self.body.strip()) and not self.image_url:
            raise ValueError("El mensaje necesita texto o una imagen")
        return self


class MessageOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    order_id: uuid.UUID
    sender_role: str
    sender_email: str | None
    body: str | None
    image_url: str | None
    created_at: datetime
