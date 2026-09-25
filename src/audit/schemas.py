from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from src.rules.schemas import RuleDBSchema
from src.correlation_rules.schemas import CorrelationRuleDBSchema
from src.users.schemas import UserOutSchema


class AuditAddSchema(BaseModel):
    author_id: int
    rule_unique_id: int
    rule_general_id: str
    action: str | None = Field(default='created')
    resource_type: str | None = None
    before_id: int | None = None
    after_id: int | None = None


class AuditOutSchema(AuditAddSchema):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True, extra="ignore")


class AuditOutWithAuthorSchema(AuditOutSchema):
    author: UserOutSchema


class ApiAuditWithAuthorSchema(BaseModel):
    total: int
    items: list[AuditOutWithAuthorSchema]


class AuditOutFullSchema(AuditOutWithAuthorSchema):
    rule: RuleDBSchema


## Correlation audit
class CorrelationAuditAddSchema(BaseModel):
    author_id: int
    correlation_unique_id: int
    correlation_id: str
    action: str | None = Field(default='created')
    resource_type: str | None = None
    before_id: int | None = None
    after_id: int | None = None


class CorrelationAuditOutSchema(CorrelationAuditAddSchema):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True, extra="ignore")


class CorrelationAuditOutWithAuthorSchema(CorrelationAuditOutSchema):
    author: UserOutSchema


class ApiCorrelationAuditWithAuthorSchema(BaseModel):
    total: int
    items: list[CorrelationAuditOutWithAuthorSchema]


class CorrelationAuditOutFullSchema(CorrelationAuditOutWithAuthorSchema):
    rule: CorrelationRuleDBSchema