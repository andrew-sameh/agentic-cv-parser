from typing import Optional, List
from pydantic import BaseModel
from datetime import date, datetime



class ExperienceBase(BaseModel):
    company_name: Optional[str] = None
    role: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
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