from src.services.base import BaseService
from src.supersession_rules.schemas import SuppressionRuleSchema, SuppressionRuleUpdateSchema, \
    SuppressionRuleCreateUpdateResultSchema, MatchFieldResponseSchema, SuppressionRequestPostSchema, \
    SuppressionRuleStatusSchema, SuppressionRuleTestSchema


class SuperSessionService(BaseService):

    async def get_supersets(self) -> list[SuppressionRuleSchema]:
        result = await self.main_backend.get("/suppression-rules")
        return [SuppressionRuleSchema.model_validate(r) for r in result]

    async def get_supersets_match_fields(self) -> MatchFieldResponseSchema:
        res = await self.main_backend.get("/reference/suppression-match-fields")
        return MatchFieldResponseSchema.model_validate(res)

    async def get_detail_superset(self, super_id: str) -> SuppressionRuleSchema:
        result = await self.main_backend.get(f"/suppression-rules/{super_id}")
        return SuppressionRuleSchema.model_validate(result)

    async def put_superset(self, super_id: str, data: SuppressionRuleUpdateSchema) -> SuppressionRuleCreateUpdateResultSchema:
        result = await self.main_backend.put(f"/suppression-rules/{super_id}", data=data)
        return SuppressionRuleCreateUpdateResultSchema.model_validate(result)

    async def post_rule(self, data: SuppressionRequestPostSchema) -> SuppressionRuleCreateUpdateResultSchema:
        result = await self.main_backend.post("/suppression-rules", data=data)
        return SuppressionRuleCreateUpdateResultSchema.model_validate(result)

    async def delete_rule(self, super_id: str):
        # схема ответа во внешнем API не описана, отдаём как есть
        return await self.main_backend.delete(f"/suppression-rules/{super_id}")

    async def set_status(self, super_id: str, data: SuppressionRuleStatusSchema):
        return await self.main_backend.patch(f"/suppression-rules/{super_id}/status", data=data)

    async def test_rule(self, data: SuppressionRuleTestSchema):
        return await self.main_backend.post("/suppression-rules/test", data=data)