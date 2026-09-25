from src.services.base import BaseService
from pydantic import BaseModel


class SequenceItemSchema(BaseModel):
    value: str
    label: str


class CorrelationGroupByFieldsSchema(BaseModel):
    value: str
    label: str
    description: str


class GroupByResponseSchema(BaseModel):
    items: list[CorrelationGroupByFieldsSchema]


class SequenceSchema(BaseModel):
    items: list[SequenceItemSchema]


class ReferenceService(BaseService):

    async def get_sequence_types(self):
        res = await self.main_backend.get("/reference/attack-types")
        attack_types = SequenceSchema.model_validate(res)

        result = await self.main_backend.get("/reference/detection-categories")
        detect_types = SequenceSchema.model_validate(result)
        return [*attack_types.items, *detect_types.items]

    async def get_group_by_fields(self):
        res = await self.main_backend.get("/reference/correlation-group-by-fields")
        return GroupByResponseSchema.model_validate(res)