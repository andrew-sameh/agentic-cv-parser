from typing import  Generic, TypeVar, Optional
from pydantic import BaseModel, Field
from datetime import datetime

T = TypeVar("T")

class ResponseBase(BaseModel, Generic[T]):
    message: Optional[str] = None
    meta: Optional[dict] = None
    data: Optional[T] = None
    status: str = "success"
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())

def create_response(
    data: T,
    message: Optional[str] = None,
    meta: Optional[dict] = None,
    status: str = "success",
) -> ResponseBase[T]:
    return ResponseBase(
        data=data,
        message=message,
        meta=meta,
        status=status
    )