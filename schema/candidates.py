from datetime import datetime
from typing import Optional, List

from pydantic import Field, BaseModel, EmailStr 
from .certificates import CertificationBase
from .education import EducationBase
from .experience import ExperienceBase
from .skills import SkillBase
from .projects import ProjectBase

class CandidateExtraction(BaseModel):
    """
    Represents the basic information of a candidate.
    """

    email: Optional[EmailStr] = Field(
        default=None, 
        description="The email address of the candidate. Must be a valid email format."
    )
    full_name: Optional[str] = Field(
        default=None, 
        description="The full name of the candidate including first and last name."
    )
    country: Optional[str] = Field(
        default=None, 
        description="The country of residence of the candidate."
    )
    location: Optional[str] = Field(
        default=None, 
        description="The city or detailed location of the candidate."
    )
    phone: Optional[str] = Field(
        default=None, 
        description="The phone number of the candidate including country code if available."
    )
   
class CandidateBase(BaseModel):
    email: EmailStr | str  # str added to make it easier on the OCR
    full_name:str  
    country:Optional[str] = None
    location: Optional[str] = None
    phone: Optional[str] = None
    status: Optional[str] = None
    resume_url: Optional[str] = None
    embeddings_namespace: Optional[str] = None
    content: Optional[str] = None

class CandidateCreate(CandidateBase):
    pass

class CandidateUpdate(BaseModel):
    email: Optional[EmailStr | str] = None # str added to make it easier on the OCR
    full_name: Optional[str] = None
    country: Optional[str] = None
    location: Optional[str] = None
    phone: Optional[str] = None
    status: Optional[str] = None
    hired: Optional[bool] = None
    resume_url: Optional[str] = None
    content: Optional[str] = None
    embeddings_namespace: Optional[str] = None

class CandidateResponse(CandidateBase):
    id: int
    hired: bool
    educations: List[EducationBase] = []
    experiences: List[ExperienceBase] = []
    projects: List[ProjectBase] = []
    certifications: List[CertificationBase] = []
    skills: List[SkillBase] = []
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True