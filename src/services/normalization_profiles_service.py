from src.services.base import BaseService
from src.normalization_profiles.schemas import NormalizationProfileSchema, NormalizationProfileTestSchema


class NormalizationProfileService(BaseService):

    async def get_profiles(self, enabled_only: bool):
        return await self.main_backend.get(
            "/normalization-profiles",
            params={"enabled_only": str(enabled_only).lower()},
        )

    async def get_profile(self, profile_name: str):
        return await self.main_backend.get(f"/normalization-profiles/{profile_name}")

    async def post_profile(self, data: NormalizationProfileSchema):
        return await self.main_backend.post("/normalization-profiles", data=data)

    async def put_profile(self, profile_name: str, data: NormalizationProfileSchema):
        return await self.main_backend.put(f"/normalization-profiles/{profile_name}", data=data)

    async def del_profile(self, profile_name: str):
        return await self.main_backend.delete(f"/normalization-profiles/{profile_name}")

    async def test_profile(self, data: NormalizationProfileTestSchema):
        return await self.main_backend.post("/normalization-profiles/test", data=data)

    async def get_fields(self):
        return await self.main_backend.get("/normalization-fields")
