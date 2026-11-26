from typing import Literal, Optional, Any

from pydantic import BaseModel, ConfigDict, Field
from src.rules.models import RuleSeverityHintEnum, SeverityHintEnum
from datetime import datetime


class RuleConditionSchema(BaseModel):
    """Условие правила (RuleCondition в API движка)"""
    field: str
    operator: Literal["contains", "equals", "startswith", "endswith"] = "contains"
    value: str
    case_sensitive: bool = False


class RuleBaseSchema(BaseModel):
    """Поля правила с дефолтами как в DetectionRule API движка.
    Нестрогая версия — для чтения из ES/PG, где старые документы могут быть неполными."""
    rule_id: str
    enabled: bool = True
    rule_type: str | None = "payload_pattern"
    scope: str | None = "generic"
    match_type: str | None = "contains"
    pattern: str = ""
    fields: list[str] = Field(default_factory=list)
    case_sensitive: bool = False
    condition_mode: Literal["all", "any"] = "all"
    conditions: list[RuleConditionSchema] = Field(default_factory=list)
    category: str | None = None
    attack_type: str | None = None
    scenario_type: str | None = None
    mitre_ids: list[str] = Field(default_factory=list)
    tactics: list[str] = Field(default_factory=list)
    severity_hint: RuleSeverityHintEnum = Field(
        RuleSeverityHintEnum.AUTO,
        description="Критичность: auto (по умолчанию — определяет движок), info, low, medium, high, critical",
    )
    confidence: int | None = Field(70, ge=0, le=100)
    description: str | None = None
    explanation_template: str | None = None
    recommendations: list[str] = Field(default_factory=list)
    enabled_reason: str | None = None
    false_positive_notes: str | None = None
    tags: list[str] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True, extra="ignore")


class RuleRequestCreateUpdateSchema(RuleBaseSchema):
    """Тело запроса на создание/изменение: category, attack_type, description обязательны, как в API движка"""
    category: str
    attack_type: str
    description: str


class RuleSetStatusSchema(BaseModel):
    enabled: bool


class RuleSetStatusApiResponseSchema(BaseModel):
    success: bool
    rule: "RuleESSchema"


class RuleInDbSchema(RuleBaseSchema):
    created_at: datetime
    updated_at: datetime
    unique_id: int


# Пример правила для OpenAPI (ответы ручек правил обнаружения)
RULE_ES_EXAMPLE: dict[str, Any] = {
    "rule_id": "web_sqli_union_select",
    "enabled": True,
    "rule_type": "payload_pattern",
    "scope": "web",
    "match_type": "contains",
    "pattern": "union select",
    "fields": ["request_uri", "payloads"],
    "case_sensitive": False,
    "condition_mode": "all",
    "conditions": [
        {"field": "http_method", "operator": "equals", "value": "GET", "case_sensitive": False}
    ],
    "category": "sql_injection",
    "attack_type": "sql_injection",
    "scenario_type": "web_attack",
    "mitre_ids": ["T1190"],
    "tactics": ["Initial Access"],
    "severity_hint": "high",
    "confidence": 85,
    "description": "Попытка SQL-инъекции через UNION SELECT в URI запроса",
    "explanation_template": "В запросе к {destination_host} обнаружен фрагмент UNION SELECT",
    "recommendations": ["Проверить логи веб-приложения", "Заблокировать IP-источник на WAF"],
    "enabled_reason": None,
    "false_positive_notes": "Возможны срабатывания на сканерах безопасности из белого списка",
    "tags": ["web", "sqli"],
    "created_by": "ular",
    "updated_by": "analyst1",
    "created_at": "2026-11-20T10:15:00+06:00",
    "updated_at": "2026-11-24T09:30:00+06:00",
}


class RuleESSchema(RuleBaseSchema):   # в базе elastic храним прямо в поля created_by, upda...
    # могут отсутствовать у правил, созданных напрямую через API движка
    created_by: str | None = None
    updated_by: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None

    model_config = ConfigDict(
        from_attributes=True,
        extra='ignore',
        json_schema_extra={"examples": [RULE_ES_EXAMPLE]},
    )


class RuleDBSchema(RuleBaseSchema):
    created_at: datetime | None = None
    updated_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True, extra='ignore')


class RuleApiResponseSchema(BaseModel):
    """Страница результатов поиска правил"""
    total: int = Field(description="Всего найдено правил")
    has_next: bool = Field(description="Есть ли следующая страница")
    items: list[RuleESSchema]

    model_config = ConfigDict(json_schema_extra={
        "examples": [{"total": 1, "has_next": False, "items": [RULE_ES_EXAMPLE]}]
    })


class RuleDeleteResponseSchema(BaseModel):
    """Результат удаления правила (ответ Elasticsearch)"""
    id: str = Field(alias="_id", description="rule_id удалённого правила")
    result: str = Field(description="Результат операции в ES")

    model_config = ConfigDict(
        populate_by_name=True,
        json_schema_extra={"examples": [{"_id": "web_sqli_union_select", "result": "deleted"}]},
    )


class Event(BaseModel):
    """Тестовое событие — NormalizedEvent движка (все поля необязательны)"""
    timestamp: Optional[datetime] = Field(None, description="ISO 8601 timestamp")
    timestamp_raw: Optional[str] = None

    # Сетевые параметры
    source_ip: Optional[str] = None
    source_user: Optional[str] = None
    source_host: Optional[str] = None
    destination_ip: Optional[str] = None
    destination_host: Optional[str] = None
    src_port: Optional[int] = None
    dst_port: Optional[int] = None
    protocol: Optional[str] = None
    observer_host: Optional[str] = None

    # Правила и сигнатуры
    rule_id: Optional[str] = None
    rule_level: Optional[int] = None
    rule_name: Optional[str] = None
    rule_groups: list[str] = Field(default_factory=list)
    signature: Optional[str] = None
    signature_id: Optional[str] = None
    attack_name: Optional[str] = None

    # MITRE ATT&CK
    mitre_ids: list[str] = Field(default_factory=list)
    mitre_tactics: list[str] = Field(default_factory=list)
    mitre_techniques: list[str] = Field(default_factory=list)

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
    recommendations: list[str] = Field(default_factory=list)

    # Источник логов и Вендор
    source_id: Optional[str] = None
    organization_id: Optional[str] = None
    normalization_profile: Optional[str] = None
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
    payloads: list[str] = Field(default_factory=list)
    payload_type: Optional[str] = None
    payload_indicators: list[str] = Field(default_factory=list)

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

    # Произвольные данные
    custom_fields: dict[str, Any] = Field(default_factory=dict)
    raw: dict[str, Any] = Field(default_factory=dict)

class TestRuleSchema(BaseModel):
    rule: RuleRequestCreateUpdateSchema
    event: Event


class TestRuleResponseSchema(BaseModel):
    matched: bool = Field(description="Сработало ли правило на событии")
    rule_id: str

    model_config = ConfigDict(json_schema_extra={
        "examples": [{"matched": True, "rule_id": "web_sqli_union_select"}]
    })


class DetectionCategoryCreateSchema(BaseModel):
    """Тело POST /detection-categories (DetectionCategoryCreate движка)"""
    category: str = Field(..., min_length=1, description="Код категории, например path_traversal")
    scope: str = Field(..., min_length=1, description="Область применения — из GET /api/rules/enums/detection-scopes")
    name: str = Field(..., min_length=1, description="Отображаемое название")
    description: str = Field("", description="Описание категории")
    default_attack_type: str = Field(..., min_length=1, description="attack_type по умолчанию — из GET /api/attack-types/")
    default_scenario_type: Optional[str] = Field(
        None, description="scenario_type по умолчанию — из GET /api/correlation-rules/scenario-types"
    )
    default_severity: SeverityHintEnum = Field(SeverityHintEnum.MEDIUM, description="Критичность по умолчанию")
    default_mitre_ids: list[str] = Field(default_factory=list, description="Техники MITRE — из GET /api/mitre/mitre")
    default_tactics: list[str] = Field(default_factory=list, description="Тактики MITRE")
    enabled: bool = True
