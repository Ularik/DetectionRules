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


    async def get_last_rule_version(self, rule_id: str) -> RuleInDbSchema:
        query = (
            select(self.model)
            .filter_by(rule_id=rule_id)
            .order_by(self.model.updated_at.desc())
        )
        res = await self.session.execute(query)
        db_obj = res.scalars().first()

        if db_obj is None:
            raise RuleNotFoundException  # Или бросьте ваше кастомное исключение (e.g., HTTPException / NotFound)

        return RuleInDbSchema.model_validate(db_obj)
