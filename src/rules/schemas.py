from pydantic import BaseModel, ConfigDict
from src.rules.models import SeverityHintEnum
from datetime import datetime


class RulePatchSchema(BaseModel):
    enabled: bool = None
    rule_type: str | None = None
    scope: str | None = None
    match_type: str | None = None
    pattern: str = None
    fields: list[str] = None
    case_sensitive: bool = None
    category: str | None = None
    attack_type: str | None = None
    scenario_type: str | None = None
    mitre_ids: list[str] = None
    tactics: list[str] = None
    severity_hint: SeverityHintEnum = None
    confidence: int | None = None
    description: str | None = None
    explanation_template: str | None = None
    recommendations: list[str] = None
    tags: list[str] = None

class RuleCreateUpdateSchema(BaseModel):
    rule_id: str
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


class RuleOutSchema(RuleCreateUpdateSchema):
    created_at: datetime
    updated_at: datetime
    created_by: str
    updated_by: str

    model_config = ConfigDict(from_attributes=True, extra='ignore')

