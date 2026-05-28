from sqlalchemy import select, insert, update, func
from sqlalchemy.exc import NoResultFound, IntegrityError
from asyncpg.exceptions import UniqueViolationError
from src.exceptions import ObjectNotFoundException, UniqueObjIsExistException
from sqlalchemy.orm import DeclarativeBase
from pydantic import BaseModel
from typing import TypeVar, Type
from src.init import elastic_manager, INDEX_ES

ModelType = TypeVar("ModelType", bound=DeclarativeBase)
SchemaType = TypeVar("SchemaType", bound=BaseModel)


class BaseRepository:
    model: Type[ModelType]
    schema: Type[SchemaType]

    def __init__(self, session_factory):
        self.session = session_factory

    async def get_objects(self, *filters, **filters_by) -> (list[BaseModel], int):
        filters_by = {k: v for k, v in filters_by.items() if v is not None}
        limit: int = filters_by.pop('limit', 10)
        offset: int = filters_by.pop('offset', 0)

        query = select(self.model).filter(*filters).filter_by(**filters_by)
        count_result = await self.session.execute(
            select(func.count()).select_from(query.subquery())
        )
        total = count_result.scalar()

        result = await self.session.execute(
            query.limit(limit).offset(offset)
        )

        return [self.schema.model_validate(res) for res in result.scalars().all()], total

    async def get_one(self, **filters) -> BaseModel:
        ((key, value),) = filters.items()
        result = await elastic_manager.elastic.get(index=INDEX_ES, id=value)
        return result["_source"]

        # query = select(self.model).filter_by(**filters)
        # result = await self.session.execute(query)
        # try:
        #     result = result.scalar_one()
        # except NoResultFound:
        #     raise ObjectNotFoundException
        # return self.schema.model_validate(result)

    async def create_object(self, schema: BaseModel) -> BaseModel:
        query = insert(self.model).values(**schema.model_dump()).returning(self.model)
        try:
            result = await self.session.execute(query)
            result = result.scalar_one()
        except IntegrityError as err:
            if isinstance(err.orig.__cause__, UniqueViolationError):
                raise UniqueObjIsExistException from err
            else:
                raise err

        response = self.schema.model_validate(result)
        await elastic_manager.elastic.index(
            index=INDEX_ES,
            id=str(response.rule_id),
            document=response.model_dump()
        )
        return response

    async def put_object(self, schema: BaseModel, **filters) -> BaseModel:
        query = (
            update(self.model)
            .values(**schema.model_dump())
            .filter_by(**filters)
            .returning(self.model)
        )
        try:
            result = await self.session.execute(query)
            result = result.scalar_one()
        except IntegrityError as err:
            if isinstance(err.orig.__cause__, UniqueViolationError):
                raise UniqueObjIsExistException from err
            else:
                raise err
        return self.schema.model_validate(result)