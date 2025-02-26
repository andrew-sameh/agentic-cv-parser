from typing import Optional, List
from pydantic import BaseModel, Field
from datetime import date, datetime

class ExperienceExtraction(BaseModel):
    """
    Represents a professional experience entry for the candidate.
    """
    company_name: Optional[str] = Field(
        default=None,
        description="The name of the company or organization where the candidate worked."
    )
    role: Optional[str] = Field(
        default=None,
        description="The job title or role held by the candidate at the company (e.g., Software Engineer, Project Manager)."
    )
    start_date: Optional[str] = Field(
        default=None,
        description="The date when the candidate started working in the role, in YYYY-MM-DD format."
    )
    end_date: Optional[str] = Field(
        default=None,
        description="The date when the candidate ended working in the role, in YYYY-MM-DD format, if applicable."
    )
    description: Optional[str] = Field(
        default=None,
        description="A brief description of the key responsibilities and accomplishments in this role."
    )
class ExperienceList(BaseModel):
    """Extracted data about multiple experiences."""
    experiences: List[ExperienceExtraction]

class ExperienceBase(BaseModel):
    company_name: Optional[str] = None
    role: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    description: Optional[str] = None

class ExperienceCreate(ExperienceBase):
    candidate_id: int 


class ExperienceUpdate(ExperienceBase):
    pass

class ExperienceOut(ExperienceBase):
    id: int
    candidate_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True