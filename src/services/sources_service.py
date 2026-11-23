from src.services.base import BaseService
from src.sources.schemas import SourceCreateUpdateSchema, SourceCreateApiResponseSchema


class SourceService(BaseService):

    async def get_sources(self):
        return await self.main_backend.get("/sources")

    async def get_source_detail(self, source_id: str):
        return await self.main_backend.get(f"/sources/{source_id}")

    async def post_source(self, data: SourceCreateUpdateSchema):
        res = await self.main_backend.post("/sources", data=data)
        return SourceCreateApiResponseSchema.model_validate(res)

    async def put_source(self, source_id: str, data: SourceCreateUpdateSchema):
        return await self.main_backend.put(f"/sources/{source_id}", data=data)

    async def del_source(self, source_id: str):
        return await self.main_backend.delete(f"/sources/{source_id}")

    async def get_source_health(self, source_id: str):
        return await self.main_backend.get(f"/sources/{source_id}/health")

    async def get_source_sample_events(self, source_id: str, size: int):
        return await self.main_backend.get(f"/sources/{source_id}/sample-events", params={"size": size})
