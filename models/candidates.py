from typing import Optional

from sqlalchemy import (
    Boolean,
    DateTime,
    Integer,
    String,
    func,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


from . import Base


class Candidates(Base):
    __tablename__ = "candidates"

    id: Mapped[int] = mapped_column(Integer, nullable=False, primary_key=True, autoincrement=True, index=True)
    email: Mapped[str] = mapped_column(String(30), index=True, unique=True)
    full_name: Mapped[str] = mapped_column(String(56), index=True)
    country: Mapped[str] = mapped_column(String(30), nullable=True)
    location: Mapped[str] = mapped_column(String(100), nullable=True)   
    phone: Mapped[str] = mapped_column(String(15), nullable=True)
    hired: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    status: Mapped[str] = mapped_column(String(15), nullable=True)
    updated_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=func.current_timestamp(), onupdate=func.current_timestamp()
    )
    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=func.current_timestamp()
    )
