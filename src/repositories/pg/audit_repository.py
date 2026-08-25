from sqlalchemy.orm import joinedload

from src.exceptions.exceptions import AuditNotFoundException
from src.repositories.pg.base import BaseRepository
from src.audit.models import Audit
from src.audit.schemas import AuditOutSchema, AuditOutWithAuthorSchema, AuditOutFullSchema
from sqlalchemy import select


class AuditRepository(BaseRepository):
    model = Audit
    schema = AuditOutSchema

    async def get_detail_audit(self, audit_id: int) -> AuditOutFullSchema:
        query = (
            select(self.model)
            .options(
                joinedload(self.model.author),
                joinedload(self.model.rule)
            )
            .filter_by(id=audit_id)
        )
        print(query.compile(compile_kwargs={"literal_binds": True}))
        res = await self.session.execute(query)
        return AuditOutFullSchema.model_validate(res.scalars().first())

    async def get_rule_audits_with_authors(self, rule_id: str) -> list[AuditOutWithAuthorSchema]:
        query = (
            select(self.model)
            .filter_by(rule_general_id=rule_id)
            .options(
                joinedload(self.model.author)
            )
            .order_by(self.model.created_at.desc())
        )
        res = await self.session.execute(query)
        return [AuditOutWithAuthorSchema.model_validate(r) for r in res.scalars().all()]

    async def get_last_audit(self, rule_id: str) -> AuditOutSchema:
        query = (
            select(self.model)
            .where(self.model.rule_general_id == rule_id)
            .order_by(self.model.created_at.desc())
        )
        res = await self.session.execute(query)
        res = res.scalars().first()
        if not res:
            raise AuditNotFoundException
        res = self.schema.model_validate(res)
        return res

