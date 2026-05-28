from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Literal
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    MODE: Literal["TEST", "LOCAL", "PROD", "DOCKER"]
    DB_NAME: str
    DB_HOST: str
    DB_HOST_DOCKER: str
    DB_USER: str
    DB_PASSWORD: str
    DB_PORT: str

    ES_HOST: str
    ES_USER: str
    ES_PASSWORD: str
    ES_VERIFY_CERTS: bool = False

    REDIS_HOST: str
    REDIS_PORT: str

    @property
    def REDIS_URL(self):
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}"

    @property
    def DB_URL(self):
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    model_config = SettingsConfigDict(env_file=BASE_DIR / ".env", extra="ignore")

    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int


settings = Settings()
