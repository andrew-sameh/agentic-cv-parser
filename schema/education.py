from typing import Optional, List
from pydantic import BaseModel
from datetime import date, datetime


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
