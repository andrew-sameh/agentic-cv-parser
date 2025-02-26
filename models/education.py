from typing import Optional

from sqlalchemy import (
    DateTime,
    Integer,
    String,
    func,
    ForeignKey
)
from sqlalchemy.orm import  Mapped, mapped_column, relationship


from . import Base

class Education(Base):
    __tablename__ = "educations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    candidate_id: Mapped[int] = mapped_column(Integer, ForeignKey("candidates.id", ondelete="CASCADE"))

    institution: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    degree: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    major: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    start_date: Mapped[Optional[str]] = mapped_column(String(30),nullable=True)
    end_date: Mapped[Optional[str]] = mapped_column(String(30),nullable=True)

    updated_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=func.current_timestamp(),
        onupdate=func.current_timestamp()
    )
    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=func.current_timestamp()
    )

    # Relationship back to Candidate
    candidate: Mapped["Candidate"] = relationship("Candidate", back_populates="educations") # noqa
