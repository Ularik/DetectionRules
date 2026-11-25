from fastapi import APIRouter, Depends
from src.rules.models import SeverityHintEnum
from src.rules.schemas import RuleApiResponseSchema, RuleESSchema
from src.services.rules_services import RuleService
from src.dependencies import DBDep, PaginationDep, get_admin_user, get_editor_user, get_current_user
from src.exceptions.schemas import error_responses
from src.rules.admin.api import router as admin_router
from src.rules.analyst.api import router as analyst_router


router = APIRouter(prefix="/rules")


router.include_router(
    admin_router,
    dependencies=[Depends(get_admin_user)],
    responses=error_responses(401, 403),
)

router.include_router(
    analyst_router,
    dependencies=[Depends(get_editor_user)],  # ADMIN тоже может пользоваться ручками аналитика
    responses=error_responses(401, 403),
)


@router.get(
    "/",
    tags=["Правила"],
    dependencies=[Depends(get_current_user)],
    response_model=RuleApiResponseSchema,
    responses=error_responses(400, 401, 503),
    summary="Поиск правил",
    description="Поиск по `pattern` и/или `description` с пагинацией. "
                "С `rule_id` возвращает страницу из одного правила (или пустую, если правила нет).",
)
async def get_rules(
        db: DBDep,
        paging: PaginationDep,
        pattern: str | None = None,
        rule_id: str | None = None,
        description: str | None = None,
        ):
    return await RuleService(db).find_rules(pattern, description, rule_id, limit=paging.limit, offset=paging.offset)


@router.get("/enums/severity-hints", tags=["Правила"], dependencies=[Depends(get_current_user)],
            response_model=list[str], responses=error_responses(401))
async def get_severity_hints():
    return [e.value for e in SeverityHintEnum]


@router.get("/enums/detection-categories", tags=["Правила"], dependencies=[Depends(get_current_user)],
            responses=error_responses(401, 502))
async def get_detection_categories(db: DBDep):
    return await RuleService(db).get_detection_categories()


@router.get("/enums/detection-scopes", tags=["Правила"], dependencies=[Depends(get_current_user)],
            responses=error_responses(401, 502))
async def get_detection_scopes(db: DBDep):
    return await RuleService(db).get_detection_scopes()


@router.get("/{rule_id}", tags=["Правила"], dependencies=[Depends(get_current_user)],
            response_model=RuleESSchema, responses=error_responses(401, 404, 503))
async def get_one_rule(
        rule_id: str,
        db: DBDep,
        ):
    rule = await RuleService(db).find_one(rule_id)
    return rule
