from typing import Optional
from pydantic import BaseModel


class TemplateOut(BaseModel):
    """Response schema for a prompt template."""

    id: int
    name: str
    description: str
    prompt_text: str
    category: str
    language: str
    tags: Optional[str] = ""
    preview_url: Optional[str] = None
    usage_count: int
    is_builtin: bool
    created_at: Optional[str] = None

    class Config:
        from_attributes = True


class TemplateCreate(BaseModel):
    """Request schema for creating a user template."""

    name: str
    description: str
    prompt_text: str
    category: str
    language: str = "en"
    tags: str = ""
