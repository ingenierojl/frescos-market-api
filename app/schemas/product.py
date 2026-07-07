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
    active: bool


class ProductCreate(BaseModel):
    slug: str
    name: str
    unit: str
    price: int
    category: str
    photo_url: str
    stock: int | None = None
    active: bool = True


class ProductUpdate(BaseModel):
    name: str | None = None
    unit: str | None = None
    price: int | None = None
    category: str | None = None
    photo_url: str | None = None
    stock: int | None = None
    active: bool | None = None
