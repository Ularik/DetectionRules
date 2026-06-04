from watchfiles import awatch
from src.exceptions import ObjectNotFoundException
from src.services.base import BaseService
from src.rules.schemas import RuleCreateUpdateSchema, RulePatchSchema
from datetime import datetime


class RuleService(BaseService):
    async def get_rule(self, rule_id: str) -> dict | None:
        return await self.es.rulesRepository.get_by_id(rule_id)

    async def find_rules(self,
                         pattern: str = None,
                         description: str = None,
                         rule_id: str = None,
                         limit: int = 10,
                         offset: int = 0) -> dict | None:
        text = pattern or description

        if rule_id:
            return await self.es.rulesRepository.get_by_id(doc_id=rule_id)
        return await self.es.rulesRepository.search_rules(text=text, limit=limit, offset=offset)

    async def create_rule(self, rule_id: str, data: RuleCreateUpdateSchema) -> dict:
        data = data.model_dump()

        data['created_at'] = datetime.now()
        data['updated_at'] = datetime.now()
        data['created_by'] = 'ular'
        data['updated_by'] = 'ular'

        return await self.es.rulesRepository.create(rule_id, data)

    async def update_rule(self, rule_id: str, data: RuleCreateUpdateSchema | RulePatchSchema, exclude_unset: bool = True):
        data = data.model_dump(exclude_unset=exclude_unset)
        data['updated_by'] = 'ular'
        data['updated_at'] = datetime.now()
        return await self.es.rulesRepository.update(doc_id=rule_id, body=data)

    async def delete(self, rule_id: str):
        return await self.es.rulesRepository.delete(doc_id=rule_id)
