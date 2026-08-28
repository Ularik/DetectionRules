from sqlalchemy import select
from src.exceptions.exceptions import  RuleNotFoundException
from src.repositories.pg.base import BaseRepository
from src.rules.models import DetectionRuleModel
from src.rules.schemas import RuleInDbSchema


class RuleRepository(BaseRepository):
    model = DetectionRuleModel
    schema = RuleInDbSchema

    async def get_objects(self, *filters, **filters_by) -> (list[RuleInDbSchema], int):
        filters = [*filters]

        if 'description' in filters_by and filters_by['description']:
            filter_one = self.model.description.ilike(f"%{filters_by.pop('description')}%")
            filters.append(filter_one)
        if 'pattern' in filters_by and filters_by['pattern']:
            filter_two = self.model.pattern.ilike(f"%{filters_by.pop('pattern')}%")
            filters.append(filter_two)

        return await super().get_objects(*filters, **filters_by)

    async def get_current_rule_rule_id(self, unique_id: int) -> str:
        query = (
            select(self.model.rule_id)
            .select_from(self.model)
            .filter_by(unique_id=unique_id)
        )
        res = await self.session.execute(query)
        rule_id = res.scalar()

        if rule_id is None:
            raise RuleNotFoundException  # Или бросьте ваше кастомное исключение (e.g., HTTPException / NotFound)

        return rule_id
