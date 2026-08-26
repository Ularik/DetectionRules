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
class RuleRequestCreateSchema(RuleBaseSchema):
    rule_id: str


# 3. Схема обновления (без rule_id, но с служебными полями)
class RuleUpdateSchema(RuleBaseSchema):
    created_by: str
    updated_by: str


class RuleInDbSchema(RuleRequestCreateSchema):
    created_at: datetime
    updated_at: datetime
    unique_id: int


class RuleESSchema(RuleRequestCreateSchema):
    created_by: str
    updated_by: str
    created_at: datetime | None = None
    updated_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True, extra='ignore')


class RuleDBSchema(RuleRequestCreateSchema):
    created_at: datetime | None = None
    updated_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True, extra='ignore')

class RuleUpdateElasticSchema(RuleRequestCreateSchema):
    updated_by: str | None = None
    updated_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True, extra='ignore')


class RuleApiResponseSchema(BaseModel):
  total: int
  has_next: bool
  items: list[RuleESSchema]
