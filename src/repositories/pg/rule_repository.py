from pydantic import BaseModel
from sqlalchemy import update, select, func

from src.exceptions import ObjectNotFoundException
from src.repositories.pg.base import BaseRepository
from src.rules.models import DetectionRuleModel
from src.rules.schemas import RuleOutSchema


class RuleRepository(BaseRepository):
    model = DetectionRuleModel
    schema = RuleOutSchema

    async def get_objects(self, *filters, **filters_by) -> (list[RuleOutSchema], int):
        filters = [*filters]

        if 'description' in filters_by and filters_by['description']:
            filter_one = self.model.description.ilike(f"%{filters_by.pop('description')}%")
            filters.append(filter_one)
        if 'pattern' in filters_by and filters_by['pattern']:
            filter_two = self.model.pattern.ilike(f"%{filters_by.pop('pattern')}%")
            filters.append(filter_two)

        return await super().get_objects(*filters, **filters_by)


    async def patch_rule(self, rule_id) -> RuleOutSchema:
        query = select(self.model).filter_by(rule_id=rule_id)
        result = await self.session.execute(query)
        rule = result.scalar_one_or_none()

        if rule is None:
            raise ObjectNotFoundException

        rule.enabled = not rule.enabled
        return self.schema.model_validate(rule)
