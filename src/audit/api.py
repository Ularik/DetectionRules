from fastapi import APIRouter
from src.dependencies import DBDep, PaginationDep
from src.services.audit_services import AuditService

router = APIRouter(prefix="/audits", tags=["Истороия изменений"])


@router.get("/rule/{rule_id}")
async def get_rule_audits_with_authors(
        db: DBDep,
        rule_id: str,
        paging: PaginationDep
):
    res = await AuditService(db).get_audits_with_authors(rule_general_id=rule_id, limit=paging.limit, offset=paging.offset)
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