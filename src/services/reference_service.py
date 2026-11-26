from contextlib import asynccontextmanager

import aiohttp
from fastapi import HTTPException, status

from src.attack_types.schemas import (
    AttackTypeCreateSchema,
    AttackTypeDeleteResponseSchema,
    AttackTypeResponseSchema,
    AttackTypeUpdateSchema,
)
from src.correlation_rules.schemas import (
    GroupByResponseSchema,
    ScenarioTypeCreateResponseSchema,
    ScenarioTypeCreateSchema,
    ScenarioTypeDeleteResponseSchema,
    ScenarioTypesResponseSchema,
    ScenarioTypeUpdateSchema,
    SequenceItemSchema,
    SequenceSchema,
)
from src.rules.schemas import DetectionCategoryCreateSchema
from src.services.base import BaseService


@asynccontextmanager
async def _reference_errors_guard():
    """Понятные ошибки записи в справочник вместо общих сообщений обработчика.

    403 движка — попытка изменить/удалить системное (или несуществующее) значение; общий обработчик
    превратил бы его в 502. 409 — значение с таким value уже есть.
    """
    try:
        yield
    except aiohttp.ClientResponseError as err:
        if err.status == status.HTTP_409_CONFLICT:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Значение с таким value уже есть в справочнике",
            ) from err
        if err.status == status.HTTP_403_FORBIDDEN:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Значение не найдено или является системным: системные значения справочника "
                       "изменять и удалять нельзя",
            ) from err
        raise


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

    # ---------- типы сценариев ----------

    async def get_scenario_types(self) -> ScenarioTypesResponseSchema:
        res = await self.main_backend.get("/reference/scenario-types")
        return ScenarioTypesResponseSchema.model_validate(res)

    async def create_scenario_type(self, data: ScenarioTypeCreateSchema) -> ScenarioTypeCreateResponseSchema:
        async with _reference_errors_guard():
            res = await self.main_backend.post("/reference/scenario-types", data=data)
        return ScenarioTypeCreateResponseSchema.model_validate(res)

    async def update_scenario_type(self, value: str, data: ScenarioTypeUpdateSchema) -> ScenarioTypeCreateResponseSchema:
        async with _reference_errors_guard():
            res = await self.main_backend.put(f"/reference/scenario-types/{value}", data=data)
        return ScenarioTypeCreateResponseSchema.model_validate(res)

    async def delete_scenario_type(self, value: str) -> ScenarioTypeDeleteResponseSchema:
        async with _reference_errors_guard():
            res = await self.main_backend.delete(f"/reference/scenario-types/{value}")
        return ScenarioTypeDeleteResponseSchema.model_validate(res)

    # ---------- типы атак ----------

    async def create_attack_type(self, data: AttackTypeCreateSchema) -> AttackTypeResponseSchema:
        async with _reference_errors_guard():
            res = await self.main_backend.post("/reference/attack-types", data=data)
        return AttackTypeResponseSchema.model_validate(res)

    async def update_attack_type(self, value: str, data: AttackTypeUpdateSchema) -> AttackTypeResponseSchema:
        async with _reference_errors_guard():
            res = await self.main_backend.put(f"/reference/attack-types/{value}", data=data)
        return AttackTypeResponseSchema.model_validate(res)

    async def delete_attack_type(self, value: str) -> AttackTypeDeleteResponseSchema:
        async with _reference_errors_guard():
            res = await self.main_backend.delete(f"/reference/attack-types/{value}")
        return AttackTypeDeleteResponseSchema.model_validate(res)

    # ---------- категории обнаружения ----------

    async def create_detection_category(self, data: DetectionCategoryCreateSchema):
        # Схема ответа в OpenAPI движка пустая, ответ отдаётся как есть
        return await self.main_backend.post("/detection-categories", data=data)
