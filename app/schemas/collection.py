from typing import Optional
from pydantic import BaseModel
from app.schemas.generation import GenerationOut


class CollectionCreate(BaseModel):
    """Request schema for creating a collection."""

    name: str
    description: Optional[str] = None


class CollectionUpdate(BaseModel):
    """Request schema for updating a collection."""

    name: Optional[str] = None
    description: Optional[str] = None


class CollectionOut(BaseModel):
    """Response schema for a collection."""

    id: int
    name: str
    description: Optional[str] = None
    cover_image: Optional[str] = None
    generations: list[GenerationOut] = []
    generation_count: int = 0
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

    class Config:
        from_attributes = True


class CollectionListOut(BaseModel):
    """Response schema for collection list."""

    items: list[CollectionOut]
    total: int


class AddToCollectionRequest(BaseModel):
    """Request schema for adding generations to a collection."""

    generation_id: int
