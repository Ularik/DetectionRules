from fastapi import APIRouter
from src.services.correlation_rules_service import CorrelationRuleService
from src.services.reference_service import ReferenceService
from src.dependencies import DBDep, AuthUserDep, EditorUserDep
from src.correlation_rules.schemas import (
    CorrelationRuleRequestCreateUpdateSchema,
    CorrelationRuleStatusSchema,
    CorrelationRuleTestSchema,
    CorrelationRuleTestResponseSchema,
    CorrelationRuleESSchema,
    CorrelationRuleDeleteResponseSchema,
    SequenceItemSchema,
    GroupByResponseSchema,
    ScenarioTypesResponseSchema,
    ScenarioTypeCreateSchema,
    ScenarioTypeCreateResponseSchema,
    ScenarioTypeUpdateSchema,
    ScenarioTypeDeleteResponseSchema,
)
from src.exceptions.schemas import error_responses


_FORM_HINTS = (
    "Значения полей формы: `sequence` — из GET /api/correlation-rules/sequence, "
    "`group_by` — из GET /api/correlation-rules/group-by-fields, "
    "`scenario_type` — из GET /api/correlation-rules/scenario-types, "
    "`mitre_ids` — из GET /api/mitre/mitre. "
    "`severity`: critical, high, medium, low, info; `confidence` — 0–100; `window_seconds` > 0."
)

router = APIRouter(prefix="/correlation-rules", tags=["Правила корреляции"], responses=error_responses(502, 504))


# ---------- статические пути: объявлены до /{correlation_id} ----------

@router.get("/", response_model=list[CorrelationRuleESSchema], responses=error_responses(401),
            summary="Список правил корреляции")
async def get_crules(
        db: DBDep,
        user: AuthUserDep
):
    return await CorrelationRuleService(db).get_crules()


@router.get("/sequence", response_model=list[SequenceItemSchema],
            summary="Справочник для поля sequence",
            description="Типы атак и категории детектирования, из которых строится последовательность правила.")
async def get_sequence(
        db: DBDep
):
    return await ReferenceService(db).get_sequence_types()


@router.get("/group-by-fields", response_model=GroupByResponseSchema,
            summary="Справочник для поля group_by")
async def get_group_by_fields(
        db: DBDep
):
    return await ReferenceService(db).get_group_by_fields()


@router.get("/scenario-types", response_model=ScenarioTypesResponseSchema,
            summary="Справочник для поля scenario_type")
async def get_scenario_types(
        db: DBDep
):
    return await ReferenceService(db).get_scenario_types()


@router.post("/scenario-types", response_model=ScenarioTypeCreateResponseSchema, status_code=201,
             responses=error_responses(400, 401, 403),
             summary="Добавить тип сценария в справочник scenario_type")
async def post_scenario_type(
        db: DBDep,
        user: EditorUserDep,
        data: ScenarioTypeCreateSchema
):
    """Прокси POST /reference/scenario-types движка; новое значение появится в GET /scenario-types."""
    return await ReferenceService(db).create_scenario_type(data=data)


@router.put("/scenario-types/{value}", response_model=ScenarioTypeCreateResponseSchema,
            responses=error_responses(401, 403, 404), summary="Изменить тип сценария")
async def put_scenario_type(
        db: DBDep,
        user: EditorUserDep,
        value: str,
        data: ScenarioTypeUpdateSchema
):
    """Меняются только `label` и `description`; системные типы изменить нельзя (403)."""
    return await ReferenceService(db).update_scenario_type(value=value, data=data)


@router.delete("/scenario-types/{value}", response_model=ScenarioTypeDeleteResponseSchema,
               responses=error_responses(401, 403), summary="Удалить тип сценария")
async def delete_scenario_type(
        db: DBDep,
        user: EditorUserDep,
        value: str
):
    """Удалить можно только добавленный вручную тип; на системный или несуществующий движок отвечает 403."""
    return await ReferenceService(db).delete_scenario_type(value=value)


@router.post("/", response_model=CorrelationRuleESSchema, status_code=201,
             responses=error_responses(400, 401, 403), summary="Создать правило корреляции",
             description=_FORM_HINTS)
async def post_crule(
        db: DBDep,
        user: EditorUserDep,
        data: CorrelationRuleRequestCreateUpdateSchema
):
    return await CorrelationRuleService(db).create_crule(data=data, user=user)


@router.post("/test", response_model=CorrelationRuleTestResponseSchema,
             responses=error_responses(400, 401, 403), summary="Проверить правило на инцидентах",
             description="Прогоняет правило на переданных инцидентах без сохранения.")
async def test_crule(
        db: DBDep,
        user: EditorUserDep,
        data: CorrelationRuleTestSchema
):
    return await CorrelationRuleService(db).test_crule(data=data)


# ---------- операции над конкретным правилом ----------

@router.get("/{correlation_id}", response_model=CorrelationRuleESSchema, responses=error_responses(401, 404),
            summary="Правило корреляции по id")
async def get_crule(
        db: DBDep,
        user: AuthUserDep,
        correlation_id: str
):
    return await CorrelationRuleService(db).get_crule_detail(correlation_id=correlation_id)


@router.put("/{correlation_id}", response_model=CorrelationRuleESSchema,
            responses=error_responses(400, 401, 403, 404), summary="Изменить правило корреляции",
            description="Правило передаётся целиком; correlation_id, created_*/updated_* не редактируются. "
                        + _FORM_HINTS)
async def put_crule(
        db: DBDep,
        correlation_id: str,
        user: EditorUserDep,
        data: CorrelationRuleRequestCreateUpdateSchema
):
    return await CorrelationRuleService(db).put_crule(data=data, user=user, correlation_id=correlation_id)


@router.delete("/{correlation_id}", response_model=CorrelationRuleDeleteResponseSchema,
               responses=error_responses(401, 403, 404), summary="Удалить правило корреляции")
async def delete_crule(
        db: DBDep,
        correlation_id: str,
        user: EditorUserDep
):
    return await CorrelationRuleService(db).delete_crule(user=user, correlation_id=correlation_id)


@router.patch("/{correlation_id}/status", response_model=CorrelationRuleESSchema,
              responses=error_responses(400, 401, 403, 404), summary="Включить/выключить правило корреляции",
              description="Возвращает правило в актуальном состоянии.")
async def set_crule_status(
        db: DBDep,
        correlation_id: str,
        user: EditorUserDep,
        data: CorrelationRuleStatusSchema
):
    return await CorrelationRuleService(db).set_status(user=user, correlation_id=correlation_id, data=data)
