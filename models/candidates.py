from typing import List, Optional

from sqlalchemy import (
    Boolean,
    DateTime,
    Integer,
    String,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship


from . import Base


class Candidate(Base):
    __tablename__ = "candidates"

    id: Mapped[int] = mapped_column(Integer, nullable=False, primary_key=True, autoincrement=True, index=True)
    email: Mapped[str] = mapped_column(String(30), index=True, unique=True)
    full_name: Mapped[str] = mapped_column(String(56), index=True)
    country: Mapped[str] = mapped_column(String(30), nullable=True)
    location: Mapped[str] = mapped_column(String(100), nullable=True)   
    phone: Mapped[str] = mapped_column(String(15), nullable=True)
    hired: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    status: Mapped[str] = mapped_column(String(15), nullable=True)
    resume_url: Mapped[str] = mapped_column(String(100), nullable=True)
    embeddings_namespace: Mapped[str] = mapped_column(String(100), nullable=True, unique=True, index=True)
    updated_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=func.current_timestamp(), onupdate=func.current_timestamp()
    )
    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=func.current_timestamp()
    )

    # Relationships
    educations: Mapped[List["Education"]] = relationship( # noqa
        "Education",
        back_populates="candidate",
        cascade="all, delete-orphan"
    )

    experiences: Mapped[List["Experience"]] = relationship( # noqa
        "Experience",
        back_populates="candidate",
        cascade="all, delete-orphan"
    )

    projects: Mapped[List["Project"]] = relationship( # noqa
        "Project",
        back_populates="candidate",
        cascade="all, delete-orphan"
    )

    certifications: Mapped[List["Certification"]] = relationship( # noqa
        "Certification",
        back_populates="candidate",
        cascade="all, delete-orphan"
    )

    # If using a many-to-many for skills:
    skills: Mapped[List["Skill"]] = relationship( # noqa
        "Skill",
        secondary="candidate_skills",   # name of the association table
        back_populates="candidates"
    )
    