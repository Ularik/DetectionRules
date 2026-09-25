from typing import Literal, Optional, Any

from pydantic import BaseModel, ConfigDict, Field
from src.rules.models import SeverityHintEnum
from datetime import datetime


class RuleRequestCreateUpdateSchema(BaseModel):
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

    model_config = ConfigDict(from_attributes=True, extra="ignore")


class RuleSetStatusSchema(BaseModel):
    enabled: bool


class RuleSetStatusApiResponseSchema(BaseModel):
    success: bool
    rule: "RuleESSchema"


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


class Event(BaseModel):
    timestamp: datetime = Field(..., description="ISO 8601 timestamp")
    timestamp_raw: Optional[str] = None

    # Сетевые параметры
    source_ip: Optional[str] = None
    source_user: Optional[str] = None
    source_host: Optional[str] = None
    destination_ip: Optional[str] = None
    destination_host: Optional[str] = None
    dst_port: Optional[int] = None
    observer_host: Optional[str] = None

    # Правила и сигнатуры
    rule_id: Optional[str] = None
    rule_level: Optional[int] = None
    rule_name: Optional[str] = None
    rule_groups: list[str] = Field(default_factory=[])
    signature: Optional[str] = None
    signature_id: Optional[str] = None
    attack_name: Optional[str] = None

    # MITRE ATT&CK
    mitre_ids: list[str] = Field(default_factory=[])
    mitre_tactics: list[str] = Field(default_factory=[])
    mitre_techniques: list[str] = Field(default_factory=[])

    # Детекция и классификация
    event_type: str = "unknown"
    action: Optional[str] = None
    outcome: Optional[str] = None
    detection_rule_id: Optional[str] = None
    detection_rule_description: Optional[str] = None
    detection_category: Optional[str] = None
    detection_confidence: Optional[int] = None
    severity_hint: Optional[str] = None
    attack_type: Optional[str] = None
    scenario_type: Optional[str] = None
    explanation_template: Optional[str] = None
    recommendations: list[str] = Field(default_factory=[])

    # Источник логов и Вендор
    log_source_type: Optional[str] = None
    szi_source: Optional[str] = None
    product_name: Optional[str] = None
    vendor_name: Optional[str] = None

    # HTTP параметры
    request_uri: Optional[str] = None
    url: Optional[str] = None
    http_method: Optional[str] = None
    http_status: Optional[int] = None
    user_agent: Optional[str] = None
    referrer: Optional[str] = None

    # Пейлоад
    payloads: list[str] = Field(default_factory=[])
    payload_type: Optional[str] = None
    payload_indicators: list[str] = Field(default_factory=[])

    # Системные события Windows / ОС
    event_code: Optional[str] = None
    winlog_channel: Optional[str] = None
    computer_name: Optional[str] = None

    # Процессы
    process_name: Optional[str] = None
    process_path: Optional[str] = None
    process_command_line: Optional[str] = None
    process_pid: Optional[str] = None
    parent_process_name: Optional[str] = None
    parent_process_path: Optional[str] = None
    parent_process_command_line: Optional[str] = None
    parent_process_pid: Optional[str] = None

    # Авторизация и УЗ
    target_user: Optional[str] = None
    logon_type: Optional[str] = None
    logon_id: Optional[str] = None

    # Файлы и хеши
    file_path: Optional[str] = None
    file_hash: Optional[str] = None
    md5_hash: Optional[str] = None
    sha1_hash: Optional[str] = None
    sha256_hash: Optional[str] = None

    # Системные объекты
    registry_key: Optional[str] = None
    service_name: Optional[str] = None
    task_name: Optional[str] = None

    # Произвольные сырые данные
    raw: dict[str, Any] = Field()

class TestRuleSchema(BaseModel):
    rule: RuleRequestCreateUpdateSchema
    event: Event


class TestRuleResponseSchema(BaseModel):
    matched: bool
    rule_id: str
