from src.services.base import BaseService


class DataQualityService(BaseService):

    async def get_summary(
            self,
            hours: int,
            organization_id: str | None,
            source_id: str | None,
            profile_name: str | None,
    ):
        params = {
            "hours": hours,
            "organization_id": organization_id,
            "source_id": source_id,
            "profile_name": profile_name,
        }
        return await self.main_backend.get("/data-quality/summary", params=params)

    async def get_sources(self, hours: int, organization_id: str | None, profile_name: str | None):
        params = {"hours": hours, "organization_id": organization_id, "profile_name": profile_name}
        return await self.main_backend.get("/data-quality/sources", params=params)

    async def get_source(
            self,
            source_id: str,
            hours: int,
            organization_id: str | None,
            profile_name: str | None,
    ):
        params = {"hours": hours, "organization_id": organization_id, "profile_name": profile_name}
        return await self.main_backend.get(f"/data-quality/sources/{source_id}", params=params)
