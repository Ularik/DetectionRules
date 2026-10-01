from src.incidents.schemas import IncidentParams, IncidentEventResponseSchema
from src.services.base import BaseService
from src.incidents.schemas import IncidentSchema


class IncidentService(BaseService):

    async def get_incidents(self, params: IncidentParams):
        return await self.main_backend.get("/hunting/incidents", params=params.model_dump(exclude_none=True))

    async def get_detail_incident(self, inc_id: str):
        res = await self.main_backend.get(f"/hunting/incidents/{inc_id}")
        return IncidentSchema.model_validate(res)

    async def get_incident_events(self, inc_id: str, page: int = 1, size: int = 10):
        res = await self.main_backend.get(f"/hunting/incidents/{inc_id}/events", params={
            "page": page,
            "size": size
        })
        return IncidentEventResponseSchema.model_validate(res)

    async def patch_incident(self, inc_id: str, analyst_status: str):
        await self.main_backend.patch(f"/hunting/incidents/{inc_id}/status", data={"analyst_status": analyst_status})
