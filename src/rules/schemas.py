from pydantic import BaseModel, ConfigDict
from src.rules.models import SeverityHintEnum
from datetime import datetime


class RuleBaseSchema(BaseModel):
    enabled: bool
    rule_type: str | None = None
    scope: str | None = None
    match_type: str | None = None
    pattern: str
    fields: list[str]
    case_sensitive: bool
    category: str | None = None
    attack_type: str | None = None
    scenario_type: str | None = None
    mitre_ids: list[str]
    tactics: list[str]
    severity_hint: SeverityHintEnum
    confidence: int | None = None
    description: str | None = None
    explanation_template: str | None = None
    recommendations: list[str]
    tags: list[str]

    model_config = ConfigDict(from_attributes=True, extra="ignore")


# 2. Схема создания (добавляем rule_id)
class RuleRequestCreateUpdateSchema(RuleBaseSchema):
    rule_id: str


class RuleInDbSchema(RuleRequestCreateUpdateSchema):
    created_at: datetime
    updated_at: datetime
    unique_id: int


class RuleESSchema(RuleRequestCreateUpdateSchema):   # в базе elastic храним прямо в поля created_by, upda...
    created_by: str
    updated_by: str
    created_at: datetime | None
    updated_at: datetime | None

    model_config = ConfigDict(from_attributes=True, extra='ignore')


class RuleDBSchema(RuleRequestCreateUpdateSchema):
    created_at: datetime | None = None
    updated_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True, extra='ignore')


class RuleApiResponseSchema(BaseModel):
  total: int
  has_next: bool
  items: list[RuleESSchema]
