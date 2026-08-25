from fastapi import APIRouter, Response, Body
from src.users.schemas import UsersAuthSchema, UserLoginSchema
from src.services.users_service import UserService
from src.dependencies import DBDep, AuthUserDep
from src.users.models import UserRoles


router = APIRouter(prefix="/users", tags=["Пользователи"])


@router.post("/login")
async def login_user(db: DBDep, data: UserLoginSchema, response: Response):
    access_token = await UserService(db).login_user(data)
    response.set_cookie("access_token", access_token, secure=False)
    return {"access_token": access_token}


@router.post("/", summary="Добавление нового пользователя")
async def add_user(db: DBDep, data: UsersAuthSchema):
    res = await UserService(db).create_user(data)
    return res


@router.get("/")
async def get_users(db: DBDep, department_id: int | None = None):
    return await UserService(db).get_users(department_id=department_id)


@router.get("/roles")
async def get_users_roles_list():
    return [role.value for role in UserRoles]

@router.get("/me")
async def get_me(db: DBDep, user: AuthUserDep):
    user = await UserService(db).get_user(id=user.user_id)
    return user

@router.get("/{id}")
async def get_me(db: DBDep, id: int):
    user = await UserService(db).get_user(id=id)
    return user

@router.post("/logout")
async def logout(response: Response):
    response.delete_cookie("access_token")
    return {"success": "Вы вышли из аккаунта"}
