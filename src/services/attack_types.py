from src.services.base import BaseService
from src.attack_types.schemas import AttackApiResponseSchema


class AttackTypesService(BaseService):

    async def get_attack_types(self):
        res = await self.main_backend.get("/reference/attack-types")
        return AttackApiResponseSchema.model_validate(res)