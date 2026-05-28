from fastapi import Depends
from pydantic import BaseModel, Field
from typing import Annotated

from src.utils.utils import DbManager
from src.database import AsyncSession


class Pagination(BaseModel):
    limit: int = Field(10, gt=0, lt=20)
    offset: int = Field(0, ge=0)


PaginationDep = Annotated[Pagination, Depends(Pagination)]


async def get_db():
    async with DbManager(session_factory=AsyncSession) as db:
        yield db


DBDep = Annotated[DbManager, Depends(get_db)]
