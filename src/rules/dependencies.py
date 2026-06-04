from fastapi import Depends
from pydantic import BaseModel, Field
from typing import Annotated
from src.repositories.elastic.rule_elastic import ElasticRulesRepository
from src.utils.db_manager import DbManager
from src.database import AsyncSession
from src.init import elastic_manager
from src.utils.elastic_manager import ElasticManager


class Pagination(BaseModel):
    limit: int = Field(10, gt=0, lt=20)
    offset: int = Field(0, ge=0)


PaginationDep = Annotated[Pagination, Depends(Pagination)]


async def get_db():
    async with DbManager(session_factory=AsyncSession) as db:
        yield db


DBDep = Annotated[DbManager, Depends(get_db)]

def get_rule_elastic() -> ElasticManager:
    es_repo = ElasticManager()
    return es_repo

ElasticDep = Annotated[ElasticRulesRepository, Depends(get_rule_elastic)]