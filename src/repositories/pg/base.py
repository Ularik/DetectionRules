from sqlalchemy import select, insert, update, func, delete
from sqlalchemy.exc import NoResultFound, IntegrityError
from asyncpg.exceptions import UniqueViolationError, ForeignKeyViolationError
from src.exceptions.exceptions import ObjectNotFoundException, UniqueObjIsExistException
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.dialects.postgresql import insert as pg_insert
from pydantic import BaseModel
from typing import TypeVar, Type

ModelType = TypeVar("ModelType", bound=DeclarativeBase)
SchemaType = TypeVar("SchemaType", bound=BaseModel)




class BaseRepository:
    model: Type[ModelType] = None
    schema: Type[SchemaType] = None

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

    async def get_one(self, **filters):
        query = select(self.model).filter_by(**filters)
        result = await self.session.execute(query)
        try:
            result = result.scalar_one()
        except NoResultFound:
            raise ObjectNotFoundException
        return self.schema.model_validate(result)

    async def create_object(self, data: BaseModel):
        query = insert(self.model).values(**data.model_dump()).returning(self.model)
        try:
            result = await self.session.execute(query)
            result = result.scalar_one()
        except IntegrityError as err:
            if isinstance(err.orig.__cause__, UniqueViolationError):
                raise UniqueObjIsExistException from err
            else:
                raise err

        response = self.schema.model_validate(result)
        return response

    async def edit(self, data: BaseModel, **filters):
        query = (
            update(self.model)
            .values(**data.model_dump())
            .filter_by(**filters)
            .returning(self.model)
        )
        try:
            result = await self.session.execute(query)
            row = result.scalar_one_or_none()
            if row is None:
                raise ObjectNotFoundException
        except IntegrityError as err:
            if isinstance(err.orig.__cause__, UniqueViolationError):
                raise UniqueObjIsExistException from err
            else:
                raise err
        return self.schema.model_validate(row)

    async def delete(self, **filters) -> None:
        query = delete(self.model).filter_by(**filters)
        # print(query.compile(compile_kwargs={"literal_binds": True}))
        await self.session.execute(query)

    async def check_exist_delete(self, **filters):
        query = select(self.model).filter_by(**filters)
        result = await self.session.execute(query)
        result = result.scalars().all()
        if len(result):
            return self.delete(**filters)
        else:
            raise ObjectNotFoundException

    async def add_bulk(
            self,
            items: list[BaseModel],
            *,
            conflict_columns: list[str] | None = None,
    ):
        if not items:
            return

        query = pg_insert(self.model).values([item.model_dump() for item in items])

        if conflict_columns:
            query = query.on_conflict_do_nothing(index_elements=conflict_columns)

        print(query.compile(compile_kwargs={"literal_binds": True}))
        try:
            await self.session.execute(query)
        except IntegrityError as err:
            if isinstance(err.orig.__cause__, ForeignKeyViolationError):
                raise ObjectNotFoundException from err
            else:
                raise err

    async def edit_bulk(self, data: BaseModel, *args, **kwargs):
        query = (
            update(self.model)
            .values(**data.model_dump(exclude_unset=True))
            .filter(*args)
            .filter_by(**kwargs)
            .returning(self.model)
        )

        result = await self.session.execute(query)
        return result.scalars().all()

    async def delete_bulk(self, *args, **filters):
        query = delete(self.model).filter(*args).filter_by(**filters)
        print(query.compile(compile_kwargs={"literal_binds": True}))
        await self.session.execute(query)