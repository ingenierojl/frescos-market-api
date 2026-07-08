from pydantic import BaseModel, ConfigDict, Field


class CatalogOptionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    type: str
    value: str
    sort_order: int


class CatalogOptionCreate(BaseModel):
    type: str = Field(pattern="^(unit|category|department|city)$")
    value: str = Field(min_length=1, max_length=60)
