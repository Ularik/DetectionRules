from pydantic import BaseModel, Field, ConfigDict
from typing import Literal


class UsersAuthSchema(BaseModel):
    username: str
    role: Literal["ADMIN", "ANALYST", "VIEWER"] = Field(default="VIEWER")
    password: str


class UserLoginSchema(BaseModel):
    username: str
    password: str


class UserInCookiesSchema(BaseModel):
    user_id: int
    username: str
    role: str


class UserAddSchema(BaseModel):
    username: str
    role: str
    hashed_password: bytes

    model_config = ConfigDict(from_attributes=True, extra='ignore')


class UserOutSchema(BaseModel):
    id: int
    username: str
    role: str
    model_config = ConfigDict(from_attributes=True)


class UserHashedPswdSchema(UserAddSchema):
    id: int
    model_config = ConfigDict(from_attributes=True)
