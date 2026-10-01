from src.scenarios.schema import ScenarioQueryParams, ScenarioApiResponse, ScenarioAggregateSchema
from src.services.base import BaseService


class ScenariosService(BaseService):

    async def get_scenarios(self, query_params: ScenarioQueryParams):
        res = await self.main_backend.get("/hunting/scenarios", params=query_params.model_dump(exclude_none=True))
        return ScenarioApiResponse.model_validate(res)

    async def get_detail_scenario(self, scenario_id: str):
        res = await self.main_backend.get(f"/hunting/scenarios/{scenario_id}")
        return ScenarioAggregateSchema.model_validate(res)
