from fastapi import Depends, Request, HTTPException, status
from pydantic import BaseModel, Field
from typing import Annotated
from src.services.auth_service import AuthService
from src.users.schemas import UserInCookiesSchema
from src.utils.db_manager import DbManager
from src.database import AsyncSession


class Pagination(BaseModel):
    limit: int = Field(10, gt=0, lt=20)
    offset: int = Field(0, ge=0)


PaginationDep = Annotated[Pagination, Depends(Pagination)]


async def get_db():
    async with DbManager(session_factory=AsyncSession) as db:
        yield db


DBDep = Annotated[DbManager, Depends(get_db)]


def get_token(request: Request) -> str:
    token = request.cookies.get("access_token", None)
    if not token:
        raise HTTPException(status_code=401, detail="Вы не передали токен аутентификации")
    return token


async def get_current_user(token: str = Depends(get_token)) -> UserInCookiesSchema:
    user_data = await AuthService.decode_token(token)
    return user_data


AuthUserDep = Annotated[UserInCookiesSchema, Depends(get_current_user)]

async def get_admin_user(user_data: UserInCookiesSchema = Depends(get_current_user)) -> UserInCookiesSchema:
    if user_data.role != "ADMIN":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Недостаточно прав для выполнения операции"
        )
    return user_data

async def get_analyst_user(user_data: UserInCookiesSchema = Depends(get_current_user)) -> UserInCookiesSchema:
    if user_data.role != "ANALYST":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Недостаточно прав для выполнения операции"
        )
    return user_data