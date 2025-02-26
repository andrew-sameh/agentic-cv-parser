from typing import Optional, List
from pydantic import BaseModel, Field
from datetime import date, datetime

class EducationExtraction(BaseModel):
    """
    Represents the educational background of the candidate.
    """
    institution: Optional[str] = Field(
        default=None,
        description="The name of the educational institution (e.g., Harvard University)."
    )
    degree: Optional[str] = Field(
        default=None,
        description="The type of degree obtained (e.g., Bachelor's, Master's, PhD)."
    )
    major: Optional[str] = Field(
        default=None,
        description="The major or field of study (e.g., Computer Science, Business Administration)."
    )
    start_date: Optional[str] = Field(
        default=None,
        description="The start date of the educational program in YYYY-MM-DD format, if known."
    )
    end_date: Optional[str] = Field(
        default=None,
        description="The end date of the educational program in YYYY-MM-DD format, if known."
    )

class EducationList(BaseModel):
    """Extracted data about multiple education entries."""
    education_entries: List[EducationExtraction]

class EducationBase(BaseModel):
    institution: Optional[str] = None
    degree: Optional[str] = None
    major: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None

class EducationCreate(EducationBase):
    candidate_id: int 

class EducationUpdate(EducationBase):
    pass

class EducationOut(EducationBase):
    id: int
    candidate_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
