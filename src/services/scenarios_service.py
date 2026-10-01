from src.scenarios.schema import ScenarioQueryParams, ScenarioApiResponse
from src.services.base import BaseService


class ScenariosService(BaseService):

    async def get_scenarios(self, query_params: ScenarioQueryParams):
        res = await self.main_backend.get("/hunting/scenarios", params=query_params.model_dump(exclude_none=True))
        return ScenarioApiResponse.model_validate(res)