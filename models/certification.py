from typing import Optional

from sqlalchemy import (
    Boolean,
    DateTime,
    Integer,
    String,
    func,
    ForeignKey
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


from . import Base


class Certification(Base):
    __tablename__ = "certifications"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    candidate_id: Mapped[int] = mapped_column(Integer, ForeignKey("candidates.id", ondelete="CASCADE"))

    certification_name: Mapped[Optional[str]] = mapped_column(String(150), nullable=True)
    issuing_organization: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    issue_date: Mapped[Optional[str]] = mapped_column(String(30), nullable=True)
    expiration_date: Mapped[Optional[str]] = mapped_column(String(30), nullable=True)

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
    candidate: Mapped["Candidate"] = relationship("Candidate", back_populates="certifications") # noqa
