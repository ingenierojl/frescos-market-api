from pydantic import BaseModel, ConfigDict, Field


class PaymentOptionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    label: str
    phone_or_account: str
    qr_image_url: str | None
    sort_order: int


class PaymentOptionCreate(BaseModel):
    label: str = Field(min_length=1, max_length=60)
    phone_or_account: str = Field(min_length=1, max_length=60)
    qr_image_url: str | None = None


class PaymentOptionUpdate(BaseModel):
    label: str | None = Field(default=None, min_length=1, max_length=60)
    phone_or_account: str | None = Field(default=None, min_length=1, max_length=60)
    qr_image_url: str | None = None
