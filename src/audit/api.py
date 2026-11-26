from typing import Literal

from fastapi import APIRouter, Depends, Query
from src.dependencies import DBDep, PaginationDep, get_current_user
from src.exceptions.schemas import error_responses
from src.audit.schemas import ApiCorrelationAuditWithAuthorSchema, CorrelationAuditOutFullSchema, \
    EngineAuditQuerySchema, EngineAuditSchema
from src.services.audit_services import AuditService, CorrelationAuditService, EngineAuditService

router = APIRouter(prefix="/audits", tags=["Истороия изменений"])

# действия, которые пишет CorrelationRuleService
CorrelationAuditAction = Literal["created", "updated", "status_changed", "deleted"]
# действия, которые пишет RuleService
RuleAuditAction = Literal["created", "updated"]


# ---------- журнал аудита внешнего API (до /{id}) ----------

@router.get(
    "/engine",
    dependencies=[Depends(get_current_user)],
    response_model=list[EngineAuditSchema],
    responses=error_responses(401),
    summary="Журнал аудита движка",
    description="Прокси `GET /audit` внешнего API: действия над всеми ресурсами "
                "(правила, IOC, организации, источники, активы и т.д.) со снимками до и после.",
)
async def get_engine_audits(
        db: DBDep,
        params: EngineAuditQuerySchema = Depends(),
):
    return await EngineAuditService(db).get_audits(params)


# ---------- история правил корреляции (до /{id}, иначе путь перехватит /{id}) ----------

@router.get(
    "/correlation-rules",
    tags=["Правила корреляции"],
    dependencies=[Depends(get_current_user)],
    response_model=ApiCorrelationAuditWithAuthorSchema,
    responses=error_responses(401),
    summary="История изменений всех правил корреляции",
)
async def get_correlation_audits(
        db: DBDep,
        paging: PaginationDep,
        action: CorrelationAuditAction | None = Query(default=None, description="Фильтр по действию"),
        author_id: int | None = Query(default=None, description="Фильтр по автору изменения"),
):
    return await CorrelationAuditService(db).get_audits(
        action=action, author_id=author_id, limit=paging.limit, offset=paging.offset
    )


@router.get(
    "/correlation-rules/rule/{correlation_id}",
    tags=["Правила корреляции"],
    dependencies=[Depends(get_current_user)],
    response_model=ApiCorrelationAuditWithAuthorSchema,
    responses=error_responses(401),
    summary="История изменений одного правила корреляции",
)
async def get_correlation_rule_audits(
        db: DBDep,
        correlation_id: str,
        paging: PaginationDep,
        action: CorrelationAuditAction | None = Query(default=None, description="Фильтр по действию"),
):
    return await CorrelationAuditService(db).get_audits(
        correlation_id=correlation_id, action=action, limit=paging.limit, offset=paging.offset
    )


@router.get(
    "/correlation-rules/{audit_id}",
    tags=["Правила корреляции"],
    dependencies=[Depends(get_current_user)],
    response_model=CorrelationAuditOutFullSchema,
    responses=error_responses(401, 404),
    summary="Запись истории правила корреляции",
    description="Версия правила на момент изменения и список изменённых полей относительно предыдущей версии.",
)
async def get_correlation_audit_detail(
        db: DBDep,
        audit_id: int,
):
    return await CorrelationAuditService(db).get_detail_audit(audit_id=audit_id)


# ---------- история правил обнаружения ----------

@router.get("/rule/{rule_id}")
async def get_rule_audits_with_authors(
        db: DBDep,
        rule_id: str,
        paging: PaginationDep,
        action: RuleAuditAction | None = Query(default=None, description="Фильтр по действию"),
):
    res = await AuditService(db).get_audits_with_authors(
        rule_general_id=rule_id, action=action, limit=paging.limit, offset=paging.offset
    )
    return res


@router.get("/")
async def get_audits(
        db: DBDep,
        paging: PaginationDep
):
    res = await AuditService(db).get_audits_with_authors(limit=paging.limit, offset=paging.offset)
    return res

@router.get("/{id}")
async def get_audit_detail(
        db: DBDep,
        id: int
):
    res = await AuditService(db).get_detail_audit(audit_id=id)
    return res
