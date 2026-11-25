from src.assets.schemas import AssetCreateUpdateSchema, AssetCriticality, AssetType
from src.services.base import BaseService


class AssetService(BaseService):

    async def get_assets(
            self,
            enabled_only: bool,
            asset_type: AssetType | None,
            criticality: AssetCriticality | None,
    ):
        params = {"enabled_only": enabled_only, "asset_type": asset_type, "criticality": criticality}
        return await self.main_backend.get("/assets", params=params)

    async def get_asset(self, asset_id: str):
        return await self.main_backend.get(f"/assets/{asset_id}")

    async def post_asset(self, data: AssetCreateUpdateSchema):
        return await self.main_backend.post("/assets", data=data)

    async def put_asset(self, asset_id: str, data: AssetCreateUpdateSchema):
        return await self.main_backend.put(f"/assets/{asset_id}", data=data)

    async def del_asset(self, asset_id: str):
        return await self.main_backend.delete(f"/assets/{asset_id}")
