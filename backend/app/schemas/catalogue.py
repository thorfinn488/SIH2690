from typing import List, Optional
from pydantic import BaseModel, ConfigDict


class CatalogueCreate(BaseModel):
    name: str
    category: str
    material: str
    craft: str
    description: str
    tags: List[str] = []


class CatalogueUpdate(BaseModel):
    name: Optional[str] = None
    category: Optional[str] = None
    material: Optional[str] = None
    craft: Optional[str] = None
    description: Optional[str] = None
    tags: Optional[List[str]] = None


class CatalogueResponse(BaseModel):
    id: str
    product_id: str
    name: str
    category: str
    material: str
    craft: str
    description: str
    tags: List[str]

    model_config = ConfigDict(from_attributes=True)
