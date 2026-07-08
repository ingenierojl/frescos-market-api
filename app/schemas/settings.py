from pydantic import BaseModel, ConfigDict


class AppSettingsOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    telegram_chat_id: str | None


class AppSettingsUpdate(BaseModel):
    telegram_chat_id: str | None = None
