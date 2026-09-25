from fastapi import Depends
from pydantic import BaseModel, Field
from typing import Annotated


class IocQueryParams(BaseModel):
    only_new: str | None = None
    severity: str | None = None
    ioc_type: str | None = None
    source_org: str | None = None
    ioc_value: str | None = None
    page: int = 1
    size: int = Field(ge=0, default=10, le=100)


IocQueryDep = Annotated[IocQueryParams, Depends(IocQueryParams)]