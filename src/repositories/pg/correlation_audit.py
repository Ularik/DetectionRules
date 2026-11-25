from sqlalchemy import select, func
from sqlalchemy.orm import joinedload

from src.exceptions.exceptions import AuditNotFoundException
from src.repositories.pg.base import BaseRepository
from src.audit.models import CorrelationAudit
from src.audit.schemas import (
    CorrelationAuditOutSchema,
    CorrelationAuditOutWithAuthorSchema,
    CorrelationAuditOutFullSchema,
    ApiCorrelationAuditWithAuthorSchema,
    diff_versions,
)
from src.correlation_rules.schemas import CorrelationRuleDBSchema


class CorrelationAuditRepository(BaseRepository):
    model = CorrelationAudit
    schema = CorrelationAuditOutSchema


    async def get_last_audit(self, correlation_id: str) -> CorrelationAuditOutSchema:
        query = (
            select(self.model)
            .where(self.model.correlation_id == correlation_id)
            .order_by(self.model.created_at.desc(), self.model.id.desc())
        )
        res = await self.session.execute(query)
        res = res.scalars().first()
        if not res:
            raise AuditNotFoundException
        res = self.schema.model_validate(res)
        return res

    async def get_audits(self, limit: int = 10, offset: int = 0, **filters) -> ApiCorrelationAuditWithAuthorSchema:
        """Страница истории (новые записи первыми). filters — точное совпадение по колонкам, None игнорируется."""
        filters = {k: v for k, v in filters.items() if v is not None}
        query = (
            select(self.model)
            .options(joinedload(self.model.author))
            .filter_by(**filters)
            .order_by(self.model.created_at.desc(), self.model.id.desc())
        )
        total = (await self.session.execute(
            select(func.count()).select_from(query.subquery())
        )).scalar()

        res = await self.session.execute(query.limit(limit).offset(offset))
        items = [CorrelationAuditOutWithAuthorSchema.model_validate(r) for r in res.scalars().all()]
        return ApiCorrelationAuditWithAuthorSchema(total=total, has_next=total > offset + limit, items=items)

    async def get_detail_audit(self, audit_id: int) -> CorrelationAuditOutFullSchema:
        """Запись истории с версией правила и изменениями относительно предыдущей версии (before_id)"""
        query = (
            select(self.model)
            .options(
                joinedload(self.model.author),
                joinedload(self.model.rule),
                joinedload(self.model.before).joinedload(CorrelationAudit.rule),
            )
            .filter_by(id=audit_id)
        )
        audit = (await self.session.execute(query)).scalars().first()
        if audit is None:
            raise AuditNotFoundException

        rule = CorrelationRuleDBSchema.model_validate(audit.rule)
        before_rule = (
            CorrelationRuleDBSchema.model_validate(audit.before.rule)
            if audit.before is not None and audit.before.rule is not None
            else None
        )
        return CorrelationAuditOutFullSchema.model_validate({
            **CorrelationAuditOutWithAuthorSchema.model_validate(audit).model_dump(),
            "rule": rule,
            "changes": diff_versions(before_rule, rule),
        })
