from src.repositories.pg.base import BaseRepository
from src.users.models import Users
from src.users.schemas import UserHashedPswdSchema, UserOutSchema
from sqlalchemy import select, update
from typing import Literal


class UsersRepository(BaseRepository):
    model = Users
    schema = UserOutSchema

    async def get_user_with_hashed_pswd(self, username: str) -> UserHashedPswdSchema:
        query = select(self.model).filter_by(username=username)
        result = await self.session.execute(query)
        user = result.scalars().first()
        if user:
            return UserHashedPswdSchema.model_validate(user)


    async def update_roles(self, users_ids: list[int], role: Literal["ADMIN", "ANALYST", "VIEWER"]):
        query = (
            update(self.model)
            .filter(self.model.id.in_(users_ids))
            .values(role=role)
            .returning(self.model)
        )
        await self.session.execute(query)
