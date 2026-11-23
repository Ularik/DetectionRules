from src.services.base import BaseService
from src.mitre.schemas import MitreTechniqueResponseSchema, MitreSyncResponseSchema


class MitreService(BaseService):

    async def get_technique(self):
        res = await self.main_backend.get("/mitre-mapping")
        return [MitreTechniqueResponseSchema.model_validate(r) for r in res]

    async def get_technique_detail(self, mitre_id: str) -> MitreTechniqueResponseSchema:
        res = await self.main_backend.get(f"/mitre-mapping/{mitre_id}")
        return MitreTechniqueResponseSchema.model_validate(res)

    async def sync_directory(self):
        res = await self.main_backend.post("/mitre-mapping/sync", timeout=60)
        return MitreSyncResponseSchema.model_validate(res)