from pydantic import BaseModel, ConfigDict


class AppSettingsOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    telegram_chat_id: str | None
    whatsapp_number: str | None
    business_phone: str | None
    street_address: str | None
    postal_code: str | None


class AppSettingsUpdate(BaseModel):
    telegram_chat_id: str | None = None
    whatsapp_number: str | None = None
    business_phone: str | None = None
    street_address: str | None = None
    postal_code: str | None = None


class PublicSettingsOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    whatsapp_number: str | None
    business_phone: str | None
    street_address: str | None
    postal_code: str | None
