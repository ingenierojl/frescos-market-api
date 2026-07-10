from pydantic import BaseModel, ConfigDict, Field


class ProductPhotoOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    photo_url: str
    sort_order: int


class ProductPhotoCreate(BaseModel):
    photo_url: str = Field(min_length=1, max_length=300)


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
    photos: list[ProductPhotoOut] = []


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
