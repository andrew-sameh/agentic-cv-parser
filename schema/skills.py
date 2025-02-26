from typing import Optional, List
from pydantic import BaseModel, Field
from datetime import date, datetime

class SkillExtraction(BaseModel):
    """
    Represents a skill possessed by the candidate.
    """
    name: str = Field(
        ...,
        description="The name of the skill (e.g., Python, Project Management, Data Analysis)."
    )
    category: str = Field(
        ...,
        description="The category or type of skill (e.g., Technical, Soft Skill, Management)."
    )
class SkillList(BaseModel):
    """Extracted data about multiple skills."""
    skills: List[SkillExtraction]

class SkillBase(BaseModel):
    name: str
    category: str

class SkillCreate(SkillBase):
   pass 

class SkillUpdate(SkillBase):
    pass

class SkillOut(SkillBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True