from typing import Optional, List
from pydantic import BaseModel, Field
from datetime import date, datetime

class CertificationExtraction(BaseModel):
    """
    Represents a certification obtained by the candidate.
    """
    certification_name: Optional[str] = Field(
        default=None,
        description="The name of the certification (e.g., PMP, AWS Certified Solutions Architect)."
    )
    issuing_organization: Optional[str] = Field(
        default=None,
        description="The organization or institution that issued the certification (e.g., PMI, AWS)."
    )
    issue_date: Optional[str] = Field(
        default=None,
        description="The date the certification was issued, in YYYY-MM-DD format, if known."
    )
    expiration_date: Optional[str] = Field(
        default=None,
        description="The expiration date of the certification, in YYYY-MM-DD format, if applicable."
    )

class CertificationList(BaseModel):
    """Extracted data about multiple certifications."""
    certifications: List[CertificationExtraction]

class CertificationBase(BaseModel):
    certification_name: Optional[str] = None
    issuing_organization: Optional[str] = None
    issue_date: Optional[str] = None
    expiration_date: Optional[str] = None

class CertificationCreate(CertificationBase):
    candidate_id: int 

class CertificationUpdate(CertificationBase):
    pass

class CertificationResponse(CertificationBase):
    id: int
    candidate_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True