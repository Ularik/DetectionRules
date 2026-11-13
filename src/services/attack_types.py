from src.services.base import BaseService
from src.attack_types.schemas import (
    AttackApiResponseSchema,
    AttackGroupsQueryParams,
    AttackGroupsResponseSchema,
)


class AttackTypesService(BaseService):

    async def get_attack_types(self):
        res = await self.main_backend.get("/reference/attack-types")
        return AttackApiResponseSchema.model_validate(res)

    async def get_attack_groups(self, source_ip: str, params: AttackGroupsQueryParams):
        res = await self.main_backend.get(
            f"/hunting/ip/{source_ip}",
            params=params.model_dump(mode="json", exclude_none=True),
        )
        return AttackGroupsResponseSchema.model_validate(res)
