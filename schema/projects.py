from typing import Optional, List
from pydantic import BaseModel
from datetime import date, datetime


class ProjectBase(BaseModel):
    project_name: Optional[str] = None
    description: Optional[str] = None
    technologies_used: Optional[str] = None
    link: Optional[str] = None

class ProjectCreate(ProjectBase):
    candidate_id: int 

class ProjectUpdate(ProjectBase):
    pass

class ProjectOut(ProjectBase):
    id: int
    candidate_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True