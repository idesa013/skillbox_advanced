from sqlalchemy import JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from cookbook.database import Base


class Recipe(Base):
    __tablename__ = "recipes"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(120), nullable=False, index=True)
    cooking_time: Mapped[int] = mapped_column(nullable=False, index=True)
    ingredients: Mapped[list[str]] = mapped_column(JSON, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    views: Mapped[int] = mapped_column(
        nullable=False,
        default=0,
        server_default="0",
        index=True,
    )
