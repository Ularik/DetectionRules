from src.services.base import BaseService
from src.events.schema import RawEventsQueryParamsSchema, WazuhEventApiResponseSchema, WazuhEventSchema

class EventService(BaseService):

    async def get_events(self, params: RawEventsQueryParamsSchema):
        res = await self.main_backend.get("/hunting/events", params=params.model_dump(exclude_none=True))
        return WazuhEventApiResponseSchema.model_validate(res)

    async def get_event_detail(self, index_name: str, event_id: str):
        res = await self.main_backend.get(f"/hunting/events/{index_name}/{event_id}",)
        return WazuhEventSchema.model_validate(res)