from src.engine_settings.schemas import EngineSettingsSchema
from src.services.base import BaseService


class EngineSettingsService(BaseService):

    @staticmethod
    def _payload(data: EngineSettingsSchema, username: str) -> dict:
        return {**data.model_dump(mode="json"), "updated_by": username}

    async def get_settings(self):
        return await self.main_backend.get("/engine-settings")

    async def update_settings(self, data: EngineSettingsSchema, username: str):
        return await self.main_backend.put("/engine-settings", data=self._payload(data, username))

    async def validate_settings(self, data: EngineSettingsSchema, username: str):
        return await self.main_backend.post("/engine-settings/validate", data=self._payload(data, username))

    async def reset_settings(self):
        return await self.main_backend.post("/engine-settings/reset")
