from src.exceptions.exceptions import UniqueObjIsExistException
from src.users.schemas import UserLoginSchema, UserInCookiesSchema, UsersAuthSchema, UserOutSchema, UserAddSchema
from src.services.base import BaseService
from src.services.auth_service import AuthService
from fastapi import HTTPException


class UserService(BaseService):

    async def login_user(self, data: UserLoginSchema) -> str:
        user = await self.db.usersModel.get_user_with_hashed_pswd(username=data.username)
        if not user:
            raise HTTPException(status_code=401, detail="Пользователь не найден")
        if not await AuthService().verify_password(data.password, user.hashed_password):
            raise HTTPException(status_code=401, detail="Неверный пароль!")

        payload = UserInCookiesSchema(**{"user_id": user.id, "username": user.username, "role": user.role})
        access_token = await AuthService().create_access_token(payload)
        return access_token

    async def create_user(self, data: UsersAuthSchema) -> UserOutSchema:
        hashed_password = await AuthService().hash_pswd(data.password)

        new_data = UserAddSchema(
            username=data.username,
            role=data.role,
            hashed_password=hashed_password,
        )

        try:
            new_user = await self.db.usersModel.create_object(new_data)
            await self.db.save()
            return new_user
        except UniqueObjIsExistException as err:
            raise HTTPException(status_code=409, detail=err.detail)

    async def get_user(self, id: int) -> UserOutSchema:
        return await self.db.usersModel.get_one(id=id)

