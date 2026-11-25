from src.services.base import BaseService
from src.correlation_rules.schemas import SequenceSchema, SequenceItemSchema, GroupByResponseSchema, ScenarioTypesResponseSchema


class ReferenceService(BaseService):

    async def get_sequence_types(self) -> list[SequenceItemSchema]:
        res = await self.main_backend.get("/reference/attack-types")
        attack_types = SequenceSchema.model_validate(res)

        result = await self.main_backend.get("/reference/detection-categories")
        detect_types = SequenceSchema.model_validate(result)
        return [*attack_types.items, *detect_types.items]

    async def get_group_by_fields(self) -> GroupByResponseSchema:
        res = await self.main_backend.get("/reference/correlation-group-by-fields")
        return GroupByResponseSchema.model_validate(res)

    async def get_scenario_types(self) -> ScenarioTypesResponseSchema:
        res = await self.main_backend.get("/reference/scenario-types")
        return ScenarioTypesResponseSchema.model_validate(res)
