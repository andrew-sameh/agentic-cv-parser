from typing import Optional, List
from pydantic import BaseModel, Field
from datetime import date, datetime

class ProjectExtraction(BaseModel):
    """
    Represents a project completed by the candidate.
    """
    project_name: Optional[str] = Field(
        default=None,
        description="The name of the project (e.g., Inventory Management System, E-commerce Website)."
    )
    description: Optional[str] = Field(
        default=None,
        description="A brief description of the project, including its purpose, goals, and key features."
    )
    technologies_used: Optional[str] = Field(
        default=None,
        description="The technologies, tools, or programming languages used in the project (e.g., Python, React, AWS)."
    )
    link: Optional[str] = Field(
        default=None,
        description="A URL link to the project, if applicable (e.g., GitHub repository, live demo)."
    )
class ProjectList(BaseModel):
    """Extracted data about multiple projects."""
    projects: List[ProjectExtraction]

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