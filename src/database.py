from src.config import settings
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import NullPool

DB_URL = settings.DB_URL

db_params = {}
if settings.MODE == "TEST":
    db_params = {"poolclass": NullPool}


if settings.MODE == "DOCKER":
    DB_URL = DB_URL.replace(settings.DB_HOST, settings.DB_HOST_DOCKER)

engine = create_async_engine(DB_URL, echo=False, **db_params)  # по умолчанию держит 15 соединений
engine_null_pool = create_async_engine(
    DB_URL, poolclass=NullPool
)  # не содержит соединений, открыл - сразу закрыл


AsyncSession = async_sessionmaker(
    engine, expire_on_commit=False
)  # возвращает одно соединение для работы с БД
AsyncSessionNullPool = async_sessionmaker(engine_null_pool, expire_on_commit=False)


class Base(DeclarativeBase):
    pass
