from typing import List, Optional
from sqlalchemy import Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class Collection(Base):
    __tablename__ = "collections"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    cover_image: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    created_at: Mapped[str] = mapped_column(Text, default=func.now())
    updated_at: Mapped[str] = mapped_column(Text, default=func.now())

    # Relationships
    generations = relationship("Generation", back_populates="collection")
