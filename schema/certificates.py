from typing import Optional, List
from pydantic import BaseModel
from datetime import date, datetime


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