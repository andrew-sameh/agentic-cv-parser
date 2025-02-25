from math import ceil
from collections.abc import Sequence
from typing import  Generic, TypeVar, Optional
from pydantic import BaseModel, Field
from datetime import datetime
from fastapi_pagination import Page, Params
from fastapi_pagination.bases import AbstractPage, AbstractParams

T = TypeVar("T")

class PageBase(Page[T], Generic[T]):
    previous_page: int | None = Field(
        default=None, description="Page number of the previous page"
    )
    next_page: int | None = Field(
        default=None, description="Page number of the next page"
    )

class ResponseBase(BaseModel, Generic[T]):
    message: Optional[str] = None
    meta: Optional[dict] = None
    data: Optional[T] = None
    status: str = "success"
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())

class ResponseBasePaginated(AbstractPage[T], Generic[T]):
    message: str | None = "Data paginated correctly"
    meta: dict = {}
    data: PageBase[T]
    status: str = "success"
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())

    __params_type__ = Params  # Set params related to Page

    @classmethod
    def create(
        cls,
        items: Sequence[T],
        total: int,
        params: AbstractParams,
    ) -> PageBase[T] | None:
        if params.size is not None and total is not None and params.size != 0:
            pages = ceil(total / params.size)
        else:
            pages = 0

        return cls(
            data=PageBase[T](
                items=items,
                page=params.page,
                size=params.size,
                total=total,
                pages=pages,
                next_page=params.page + 1 if params.page < pages else None,
                previous_page=params.page - 1 if params.page > 1 else None,
            )
        )

def create_response(
    data: T,
    message: Optional[str] = None,
    meta: Optional[dict] = None,
    status: str = "success",
) ->( ResponseBase[T]
    | ResponseBasePaginated[T]
):
    if isinstance(data, PageBase):
        return ResponseBasePaginated(
            data=data,
            message=message,
            meta=meta,
            status=status
        )
    else:
        return ResponseBase(
            data=data,
            message=message,
            meta=meta,
            status=status
        )