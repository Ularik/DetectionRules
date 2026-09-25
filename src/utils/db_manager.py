from src.repositories.pg.rule_repository import RuleRepository
from src.repositories.pg.users import UsersRepository
from src.repositories.pg.audit_repository import AuditRepository
from src.repositories.pg.correlation_rule_repository import CorrelationRuleRepository
from src.repositories.pg.correlation_audit import CorrelationAuditRepository


class DbManager:
    def __init__(self, session_factory):
        self.session_factory = session_factory

    async def __aenter__(self):
        self.session = self.session_factory()
        self.ruleModel = RuleRepository(self.session)
        self.usersModel = UsersRepository(self.session)
        self.auditModel = AuditRepository(self.session)
        self.correlationModel = CorrelationRuleRepository(self.session)
        self.correlationAuditModel = CorrelationAuditRepository(self.session)
        return self

    async def __aexit__(self, *args):
        await self.session.rollback()
        await self.session.close()

    async def save(self):
        await self.session.commit()


