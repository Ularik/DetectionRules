from sqlalchemy import select

from src.exceptions.exceptions import AuditNotFoundException
from src.repositories.pg.base import BaseRepository
from src.audit.models import CorrelationAudit
from src.audit.schemas import CorrelationAuditOutSchema


class CorrelationAuditRepository(BaseRepository):
    model = CorrelationAudit
    schema = CorrelationAuditOutSchema


    async def get_last_audit(self, correlation_id: str) -> CorrelationAuditOutSchema:
        query = (
            select(self.model)
            .where(self.model.correlation_id == correlation_id)
            .order_by(self.model.created_at.desc())
        )
        res = await self.session.execute(query)
        res = res.scalars().first()
        if not res:
            raise AuditNotFoundException
        res = self.schema.model_validate(res)
        return res