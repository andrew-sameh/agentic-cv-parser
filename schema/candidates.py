from utils.partial import optional
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr 

class CandidateBase(BaseModel):
    email: EmailStr
    full_name:str  
    country:Optional[str] 
    location: Optional[str]
    phone: Optional[str]
    status: Optional[str]

class CandidateCreate(CandidateBase):
    pass

class CandidateResponse(CandidateBase):
    id: int
    hired: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class CandidateUpdate(BaseModel):
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    country: Optional[str] = None
    location: Optional[str] = None
    phone: Optional[str] = None
    status: Optional[str] = None
    hired: Optional[bool] = None