from typing import Optional, List
from pydantic import BaseModel
from datetime import date, datetime

class SkillBase(BaseModel):
    name: str
    category: str

class SkillCreate(SkillBase):
    candidate_id: int 

class SkillUpdate(SkillBase):
    pass

class SkillOut(SkillBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True