from src.services.base import BaseService
from src.events.schema import RawEventsQueryParamsSchema, WazuhEventApiResponseSchema

class EventService(BaseService):

    async def get_events(self, params: RawEventsQueryParamsSchema):
        res = await self.main_backend.get("/hunting/events", params=params.model_dump(exclude_none=True))
        return WazuhEventApiResponseSchema.model_validate(res)