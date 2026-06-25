from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class GenerateRequest(BaseModel):
    """Request schema for POST /api/generate."""

    prompt: str = Field(..., min_length=1, max_length=4000, description="图片生成提示词")
    size: str = Field(default="2K", description="图片尺寸: 1K/2K/4K 或 1024x1024/1664x936/936x1664", pattern=r"^(1024x1024|1664x936|936x1664|1K|2K|4K)$")
    n: int = Field(default=1, ge=1, le=4, description="生成数量")
    seed: int = Field(default=-1, description="随机种子，-1 为随机")
    template_id: Optional[int] = Field(default=None, description="关联的提示词模板 ID")
    collection_id: Optional[int] = Field(default=None, description="添加到合集的 ID")


class ImageResult(BaseModel):
    """A single generated image result."""

    local_path: Optional[str] = None
    thumbnail_path: Optional[str] = None
    original_url: Optional[str] = None


class GenerationOut(BaseModel):
    """Response schema for a generation record."""

    id: int
    prompt: str
    model: str
    size: str
    seed: int
    n_images: int
    images: list[ImageResult] = []
    local_path: Optional[str] = None
    thumbnail_path: Optional[str] = None
    original_url: Optional[str] = None
    template_id: Optional[int] = None
    template_name: Optional[str] = None
    collection_id: Optional[int] = None
    collection_name: Optional[str] = None
    status: str
    error_message: Optional[str] = None
    created_at: Optional[str] = None

    class Config:
        from_attributes = True


class GenerationListOut(BaseModel):
    """Response schema for paginated generation list."""

    items: list[GenerationOut]
    total: int
    page: int
    pages: int


class GenerationUpdate(BaseModel):
    """Request schema for PATCH /api/generations/{id}."""

    collection_id: Optional[int] = None
