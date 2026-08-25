from fastapi import APIRouter
from src.dependencies import DBDep
from src.services.audit_services import AuditService

router = APIRouter(prefix="/audit", tags=["Истороия изменений"])


@router.get("/rule/{rule_id}")
async def get_rule_audits_with_authors(
        db: DBDep,
        rule_id: str
):
    res = await AuditService(db).get_rule_audits_with_authors(rule_id)
    return res


@router.get("/{id}")
async def get_audit_detail(
        db: DBDep,
        id: int
):
    res = await AuditService(db).get_detail_audit(audit_id=id)
    return res