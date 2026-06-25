from typing import Optional
from sqlalchemy import Integer, String, Text, ForeignKey, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class Generation(Base):
    __tablename__ = "generations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    prompt: Mapped[str] = mapped_column(Text, nullable=False)
    model: Mapped[str] = mapped_column(String(100), nullable=False, default="doubao-seedream-4-0-250828")
    size: Mapped[str] = mapped_column(String(20), nullable=False, default="1024x1024")
    seed: Mapped[int] = mapped_column(Integer, default=-1)
    n_images: Mapped[int] = mapped_column(Integer, default=1)
    local_path: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    thumbnail_path: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    original_url: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)
    template_id: Mapped[Optional[int]] = mapped_column(ForeignKey("prompt_templates.id", ondelete="SET NULL"), nullable=True)
    collection_id: Mapped[Optional[int]] = mapped_column(ForeignKey("collections.id", ondelete="SET NULL"), nullable=True)
    response_format: Mapped[str] = mapped_column(String(10), default="url")
    api_response: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="pending")
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[str] = mapped_column(Text, default=func.now())

    # Relationships
    template = relationship("PromptTemplate", back_populates="generations")
    collection = relationship("Collection", back_populates="generations")
