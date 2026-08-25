from src.repositories.elastic.base import ElasticRepository
from src.rules.schemas import RuleApiResponseSchema, RuleESSchema, RuleUpdateElasticSchema


class ElasticRulesRepository(ElasticRepository):
    INDEX = "soc-detection-rules"

    async def search_rules(self, text: str | None = None, limit: int = 10, offset: int = 0) -> RuleApiResponseSchema:
        must = []

        if text:
            must.append({
                "multi_match": {
                    "query": text,
                    "fields": ["pattern", "description"],
                    "type": "best_fields",
                    "fuzziness": "AUTO"  # допускает опечатки
                }
            })

        query = {
                "from": offset,
                "size": limit,
                "query": {"match_all": {}}}
        if must:
            query['query'] = {
                    "bool": {
                        "must": must,
                    }
                }

        items, total = await self.search(query)
        result = RuleApiResponseSchema(total=total, has_next=total > limit + offset, items=items)
        return result

    async def create_rule(self, data: RuleESSchema) -> RuleESSchema:
        res = await super().create(data.rule_id, data.model_dump())
        return RuleESSchema.model_validate(res)

    async def get_one_rule(self, doc_id: str) -> RuleESSchema:
        res = await super().get_by_id(doc_id=doc_id)
        return RuleESSchema.model_validate(res)

    async def update_rule(self, rule_id: str, data: RuleUpdateElasticSchema, exclude_unset: bool = True) -> RuleESSchema:
        res = await super().update(doc_id=rule_id, body=data.model_dump(exclude_unset=exclude_unset))
        return RuleESSchema.model_validate(res)