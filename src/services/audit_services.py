from src.services.base import BaseService
from src.audit.schemas import AuditOutSchema, AuditAddSchema, AuditOutWithAuthorSchema, AuditOutFullSchema


class AuditService(BaseService):

    async def get_rule_audits_with_authors(self, rule_id: str) -> list[AuditOutWithAuthorSchema]:
        res = await self.db.auditModel.get_rule_audits_with_authors(rule_id=rule_id)
        return res

    async def get_detail_audit(self, audit_id: int) -> AuditOutFullSchema:
        return await self.db.auditModel.get_detail_audit(audit_id=audit_id)