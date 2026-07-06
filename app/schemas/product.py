from pydantic import BaseModel, ConfigDict


class ProductOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    slug: str
    name: str
    unit: str
    price: int
    category: str
    photo_url: str
    stock: int | None
