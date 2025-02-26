from math import ceil
from collections.abc import Sequence
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

class ResponseBasePaginated(BaseModel, Generic[T]):
    message: str | None = "Data paginated correctly"
    meta: dict = {}
    data: Sequence[T]
    page: int |None = None
    size: int | None = None
    total: int | None = None
    pages: int | None = None
    status: str = "success"
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())


def create_response(
    data: T,
    message: Optional[str] = None,
    meta: Optional[dict] = None,
    status: str = "success",
) ->( ResponseBase[T]
):
    return ResponseBase(
            data=data,
            message=message,
            meta=meta,
            status=status
        )
    
def create_paginated_response(
    data: Sequence[T],
    page: int,
    size: int,
    total: int,
    meta: Optional[dict] = {},
    status: str = "success",
) -> ResponseBasePaginated[T]:
    return ResponseBasePaginated(
        data=data,
        page=page,
        size=size,
        total=total,
        pages=ceil(total / size),
        meta=meta,
        status=status
)