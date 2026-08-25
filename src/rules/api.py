from fastapi import APIRouter, Depends
from src.rules.models import SeverityHintEnum
from src.services.rules_services import RuleService
from src.dependencies import DBDep, PaginationDep, get_admin_user, get_analyst_user
from src.rules.admin.api import router as admin_router
from src.rules.analyst.api import router as analyst_router


router = APIRouter(prefix="/rules")


router.include_router(
    admin_router,
    dependencies=[Depends(get_admin_user)]
)

router.include_router(
    analyst_router,
    dependencies=[Depends(get_analyst_user)]
)


@router.get("/", tags=["Правила"])
async def get_rules(
        db: DBDep,
        paging: PaginationDep,
        pattern: str = None,
        rule_id: str = None,
        description: str = None,
        ):
    return await RuleService(db).find_rules(pattern, description, rule_id, limit=paging.limit, offset=paging.offset)


@router.get("/{rule_id}", tags=["Правила"])
async def get_one_rule(
        rule_id: str,
        db: DBDep,
        ):
    rule = await RuleService(db).find_one(rule_id)
    return rule


@router.get("/enums/severity-hints", tags=["Правила"])
async def get_severity_hints():
    return [e.value for e in SeverityHintEnum]

