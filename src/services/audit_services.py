from src.services.base import BaseService
from src.audit.schemas import AuditOutFullSchema, ApiAuditWithAuthorSchema, \
    ApiCorrelationAuditWithAuthorSchema, CorrelationAuditOutFullSchema


class AuditService(BaseService):

    async def get_audits_with_authors(
            self,
          rule_general_id: str = None,
          limit: int = 10,
          offset: int = 0,
          **kwargs
    ) -> ApiAuditWithAuthorSchema:
        if rule_general_id:
            kwargs["rule_general_id"] = rule_general_id
        res = await self.db.auditModel.get_audits(limit=limit, offset=offset, **kwargs)
        return res

    async def get_detail_audit(self, audit_id: int) -> AuditOutFullSchema:
        return await self.db.auditModel.get_detail_audit(audit_id=audit_id)

class CorrelationAuditService(BaseService):

    async def get_audits(
            self,
            correlation_id: str | None = None,
            action: str | None = None,
            author_id: int | None = None,
            limit: int = 10,
            offset: int = 0,
    ) -> ApiCorrelationAuditWithAuthorSchema:
        return await self.db.correlationAuditModel.get_audits(
            limit=limit, offset=offset, correlation_id=correlation_id, action=action, author_id=author_id
        )

    async def get_detail_audit(self, audit_id: int) -> CorrelationAuditOutFullSchema:
        return await self.db.correlationAuditModel.get_detail_audit(audit_id=audit_id)
