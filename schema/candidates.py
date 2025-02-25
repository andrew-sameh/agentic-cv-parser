from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, EmailStr 
from .certificates import CertificationBase
from .education import EducationBase
from .experience import ExperienceBase
from .skills import SkillBase
from .projects import ProjectBase
class CandidateBase(BaseModel):
    email: EmailStr
    full_name:str  
    country:Optional[str] 
    location: Optional[str]
    phone: Optional[str]
    status: Optional[str]
    resume_url: Optional[str]
    embeddings_namespace: Optional[str]

class CandidateCreate(CandidateBase):
    pass

class CandidateUpdate(BaseModel):
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    country: Optional[str] = None
    location: Optional[str] = None
    phone: Optional[str] = None
    status: Optional[str] = None
    hired: Optional[bool] = None
    resume_url: Optional[str] = None

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