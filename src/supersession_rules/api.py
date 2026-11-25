from fastapi import APIRouter, Depends
from src.dependencies import DBDep, get_editor_user
from src.exceptions.schemas import error_responses
from src.services.supersession_rules import SuperSessionService
from src.supersession_rules.schemas import SuppressionRuleUpdateSchema, SuppressionRequestPostSchema, \
    SuppressionRuleStatusSchema, SuppressionRuleTestSchema, SuppressionRuleSchema, \
    SuppressionRuleCreateUpdateResultSchema, SuppressionRuleDeleteResponseSchema, \
    SuppressionRuleTestResponseSchema, MatchFieldResponseSchema, ActionFieldResponseSchema


router = APIRouter(prefix="/supersession-rules", tags=["Правила подавления"], responses=error_responses(502, 504))


@router.get("/", response_model=list[SuppressionRuleSchema], summary="Список правил подавления")
async def get_rules(
        db: DBDep,
):
    return await SuperSessionService(db).get_supersets()


@router.post("/", dependencies=[Depends(get_editor_user)], response_model=SuppressionRuleCreateUpdateResultSchema,
             status_code=201, responses=error_responses(400, 401, 403), summary="Создать правило подавления",
             description="Ответ: `{success, rule}`, где `rule` — созданное правило с присвоенным `suppression_id`.")
async def post_rule(
        db: DBDep,
        data: SuppressionRequestPostSchema
):
    return await SuperSessionService(db).post_rule(data)


@router.post("/test", dependencies=[Depends(get_editor_user)], response_model=SuppressionRuleTestResponseSchema,
             responses=error_responses(400, 401, 403), summary="Проверить правило подавления на инциденте",
             description="Если правило не сработало: `matched=false`, `mode`, `reason` и `result` — null.")
async def test_rule(
        db: DBDep,
        data: SuppressionRuleTestSchema
):
    return await SuperSessionService(db).test_rule(data)


@router.get("/suppression-match-fields", response_model=MatchFieldResponseSchema,
            summary="Справочник полей блока match")
async def get_match_fields(
        db: DBDep,
):
    return await SuperSessionService(db).get_supersets_match_fields()


@router.get("/suppression-action-fields", response_model=ActionFieldResponseSchema,
            summary="Справочник полей блока action",
            description="Если у поля есть `values` — dropdown из них; если `reference` — значения загрузить "
                        "из указанного endpoint (для `action.attack_type` это `GET /api/attack-types`).")
async def get_action_fields(
        db: DBDep,
):
    return await SuperSessionService(db).get_supersets_action_fields()


@router.get("/{super_id}", response_model=SuppressionRuleSchema, responses=error_responses(404),
            summary="Правило подавления по ID")
async def get_detail(
        db: DBDep,
        super_id: str
):
    return await SuperSessionService(db).get_detail_superset(super_id=super_id)


@router.put("/{super_id}", dependencies=[Depends(get_editor_user)], response_model=SuppressionRuleCreateUpdateResultSchema,
            responses=error_responses(400, 401, 403, 404), summary="Изменить правило подавления",
            description="Правило передаётся целиком: `description` и `match` обязательны, неуказанные необязательные "
                        "поля сбрасываются. `action` — объект как в `POST /` (поля и значения — из "
                        "`GET /api/supersession-rules/suppression-action-fields`, `action.attack_type` — из "
                        "`GET /api/attack-types/`); строка в `action` и плоские `decision`/`risk_score`/`suppressed`/"
                        "`suppression_reason` — старый формат, оставлен для совместимости. "
                        "Ответ: `{success, rule}` — правило после изменения.")
async def put_detail(
        db: DBDep,
        super_id: str,
        data: SuppressionRuleUpdateSchema
):
    return await SuperSessionService(db).put_superset(super_id=super_id, data=data)


@router.delete("/{super_id}", dependencies=[Depends(get_editor_user)], response_model=SuppressionRuleDeleteResponseSchema,
               responses=error_responses(401, 403, 404), summary="Удалить правило подавления")
async def delete_rule(
        db: DBDep,
        super_id: str
):
    return await SuperSessionService(db).delete_rule(super_id=super_id)


@router.patch("/{super_id}/status", dependencies=[Depends(get_editor_user)],
              response_model=SuppressionRuleCreateUpdateResultSchema,
              responses=error_responses(400, 401, 403, 404), summary="Включить / выключить правило подавления",
              description="Ответ: `{success, rule}` — правило с новым значением `enabled`.")
async def set_status(
        db: DBDep,
        super_id: str,
        data: SuppressionRuleStatusSchema
):
    return await SuperSessionService(db).set_status(super_id=super_id, data=data)
