from datetime import datetime
from typing import List, Optional, Literal, Union
from pydantic import BaseModel, ConfigDict, Field, model_validator

from src.incidents.schemas import IncidentTestSchema


# ---------- схемы запросов (сверены с doc.json внешнего API, раздел Suppression) ----------

SuppressionMode = Literal["suppress"]
SuppressionDecision = Literal["malicious", "suspicious", "benign"]
SuppressionSeverity = Literal["critical", "high", "medium", "low", "info"]
SuppressionIncidentAction = Literal["block", "investigate", "monitor", "ignore"]


class SuppressionMatchSchema(BaseModel):
    """Условия совпадения (SuppressionMatch). Нужно заполнить хотя бы одно поле."""
    source_ip: Optional[str] = Field(default=None, description="IP-адрес источника (точное совпадение)")
    destination_ip: Optional[str] = Field(default=None, description="IP-адрес назначения (точное совпадение)")
    dst_port: Optional[int] = Field(default=None, ge=1, le=65535, description="Порт назначения (среди target_ports Incident)")
    observer_host: Optional[str] = Field(default=None, description="Хост-наблюдатель (точное совпадение)")
    attack_type: Optional[str] = Field(default=None, description="Тип атаки (справочник /attack-types)")
    detection_rule_id: Optional[str] = Field(default=None, description="ID правила детектирования (среди detection_rule_ids Incident)")
    category: Optional[str] = Field(default=None, description="Категория (среди detection_categories Incident)")
    paths: List[str] = Field(default_factory=list, description="Точные пути внутри события")
    path_prefixes: List[str] = Field(default_factory=list, description="Префиксы путей внутри события")
    contains: List[str] = Field(default_factory=list, description="Подстроки в тексте события (без учёта регистра)")

    @model_validator(mode="after")
    def check_at_least_one_field_present(self) -> "SuppressionMatchSchema":
        has_data = any(
            value is not None and value != []
            for value in self.model_dump().values()
        )
        if not has_data:
            raise ValueError("Хотя бы один критерий совпадения (поле) должен быть заполнен")
        return self


class SuppressionActionSchema(BaseModel):
    """Действие при срабатывании (SuppressionAction). Все переопределения необязательны."""
    mode: SuppressionMode = Field(default="suppress", description="Режим обработки (движок поддерживает только suppress)")
    attack_type: Optional[str] = Field(default=None, description="Переопределение attack_type Incident (справочник /attack-types)")
    decision: Optional[SuppressionDecision] = Field(default=None, description="Переопределение decision Incident")
    severity: Optional[SuppressionSeverity] = Field(default=None, description="Переопределение severity Incident")
    risk_score: Optional[int] = Field(default=None, ge=0, le=100, description="Переопределение risk_score Incident")
    action: Optional[SuppressionIncidentAction] = Field(default=None, description="Переопределение итогового действия Incident")
    suppressed: bool = Field(default=True, description="Признак suppressed у Incident")
    suppression_reason: Optional[str] = Field(default=None, description="Причина подавления")


# ---------- схемы ответов (сверены с фактическими ответами внешнего API /suppression-rules) ----------

class SuppressionMatchResponseSchema(BaseModel):
    """Условия совпадения в ответе: внешний API всегда отдаёт все ключи, незаданные — null / []"""
    source_ip: Optional[str] = Field(default=None, description="IP-адрес источника")
    destination_ip: Optional[str] = Field(default=None, description="IP-адрес назначения")
    dst_port: Optional[int] = Field(default=None, description="Порт назначения")
    observer_host: Optional[str] = Field(default=None, description="Хост-наблюдатель")
    attack_type: Optional[str] = Field(default=None, description="Тип атаки")
    detection_rule_id: Optional[str] = Field(default=None, description="ID правила детектирования")
    category: Optional[str] = Field(default=None, description="Категория")
    paths: List[str] = Field(default_factory=list, description="Точные пути")
    path_prefixes: List[str] = Field(default_factory=list, description="Префиксы путей")
    contains: List[str] = Field(default_factory=list, description="Подстроки в тексте события")


class SuppressionActionResponseSchema(BaseModel):
    """Действие в ответе: все переопределения необязательны и могут быть null"""
    mode: Optional[str] = Field(default="suppress", description="Режим обработки")
    attack_type: Optional[str] = Field(default=None, description="Переопределение типа атаки")
    decision: Optional[str] = Field(default=None, description="Переопределение decision (malicious|suspicious|benign)")
    severity: Optional[str] = Field(default=None, description="Переопределение severity (critical|high|medium|low|info)")
    risk_score: Optional[int] = Field(default=None, description="Переопределение risk_score (0–100)")
    action: Optional[str] = Field(default=None, description="Переопределение действия (block|investigate|monitor|ignore)")
    suppressed: bool = Field(default=True, description="Признак подавления Incident")
    suppression_reason: Optional[str] = Field(default=None, description="Причина подавления")


class SuppressionRuleSchema(BaseModel):
    suppression_id: str = Field(..., description="Уникальный идентификатор правила подавления")
    enabled: bool = Field(..., description="Статус активности правила")
    description: str = Field(..., description="Описание правила")
    reason: Optional[str] = Field(default=None, description="Причина создания правила")
    match: SuppressionMatchResponseSchema = Field(..., description="Условия срабатывания правила")
    action: SuppressionActionResponseSchema = Field(..., description="Действия при срабатывании")
    tags: List[str] = Field(default_factory=list, description="Теги")
    created_at: Optional[datetime] = Field(default=None, description="Дата и время создания")
    updated_at: Optional[datetime] = Field(default=None, description="Дата и время обновления")
    created_by: str | None = Field(default=None, description="Автор создания")
    updated_by: str | None = Field(default=None, description="Автор последнего обновления")

    model_config = ConfigDict(json_schema_extra={"examples": [{
        "suppression_id": "SUP-539A1D2A",
        "enabled": True,
        "description": "Подавление сканирования от доверенного сканера",
        "reason": "Внутренний vulnerability scanner",
        "match": {"source_ip": "10.10.10.10", "destination_ip": None, "dst_port": None, "observer_host": None,
                  "attack_type": "network_scan", "detection_rule_id": None, "category": None,
                  "paths": [], "path_prefixes": [], "contains": []},
        "action": {"mode": "suppress", "attack_type": None, "decision": None, "severity": "low",
                   "risk_score": None, "action": "ignore", "suppressed": True,
                   "suppression_reason": "Trusted vulnerability scanner"},
        "tags": ["scanner", "trusted"],
        "created_at": None, "updated_at": None, "created_by": "dev", "updated_by": "dev",
    }]})


class SuppressionRuleDeleteResponseSchema(BaseModel):
    success: bool = Field(..., description="Признак успешного удаления")
    suppression_id: str = Field(..., description="ID удалённого правила")


class SuppressionTestResultSchema(BaseModel):
    """Итоговые значения Incident после применения правила"""
    severity: Optional[str] = None
    decision: Optional[str] = None
    risk_score: Optional[int] = None
    action: Optional[str] = None
    suppressed: bool


class SuppressionRuleTestResponseSchema(BaseModel):
    matched: bool = Field(..., description="Сработало ли правило на инциденте")
    mode: Optional[str] = Field(default=None, description="Режим обработки (null, если не сработало)")
    reason: Optional[str] = Field(default=None, description="Причина срабатывания (null, если не сработало)")
    result: Optional[SuppressionTestResultSchema] = Field(
        default=None, description="Итог применения правила (null, если не сработало)")

    model_config = ConfigDict(json_schema_extra={"examples": [
        {"matched": True, "mode": "suppress", "reason": "Trusted scanner",
         "result": {"severity": "low", "decision": None, "risk_score": None, "action": None, "suppressed": True}},
        {"matched": False, "mode": None, "reason": None, "result": None},
    ]})


class SuppressionRuleUpdateSchema(BaseModel):
    """Тело PUT (SuppressionRuleUpdate). `action` — объект SuppressionAction (как в POST, рекомендуемый вариант),
    либо строка с итоговым действием (старый плоский формат вместе с decision/risk_score/suppressed/
    suppression_reason на верхнем уровне), либо null."""
    description: str = Field(..., description="Описание правила")
    reason: Optional[str] = Field(default=None, description="Причина создания правила")
    match: SuppressionMatchSchema = Field(..., description="Условия совпадения (передаётся целиком)")
    decision: Optional[SuppressionDecision] = Field(default=None, description="Переопределение decision Incident (старый плоский формат)")
    risk_score: Optional[int] = Field(default=None, ge=0, le=100, description="Переопределение risk_score Incident (старый плоский формат)")
    action: Union[SuppressionActionSchema, SuppressionIncidentAction, None] = Field(
        default=None,
        description="Блок action целиком (объект SuppressionAction, поля — из GET /api/supersession-rules/"
                    "suppression-action-fields) или, в старом формате, строка итогового действия Incident",
        examples=[{"mode": "suppress", "attack_type": "network_scan", "severity": "low", "action": "ignore",
                   "suppressed": True, "suppression_reason": "Trusted vulnerability scanner"}],
    )
    suppressed: bool = Field(default=True, description="Признак suppressed у Incident (старый плоский формат)")
    suppression_reason: Optional[str] = Field(default=None, description="Причина подавления (старый плоский формат)")
    tags: List[str] = Field(default_factory=list, description="Теги")


class SuppressionRuleCreateUpdateResultSchema(BaseModel):
    success: bool
    rule: SuppressionRuleSchema


class SuppressionRequestPostSchema(BaseModel):
    """Тело POST и правило в /test (SuppressionRuleCreate / SuppressionRuleTestData)"""
    enabled: bool = Field(default=True, description="Статус активности правила")
    description: str = Field(..., description="Описание правила")
    reason: Optional[str] = Field(default=None, description="Причина создания правила")
    match: SuppressionMatchSchema = Field(..., description="Условия срабатывания правила")
    action: SuppressionActionSchema = Field(default_factory=SuppressionActionSchema, description="Действия при срабатывании")
    tags: List[str] = Field(default_factory=list, description="Теги")


class MatchFieldSchema(BaseModel):
    field: str
    label: str
    description: str
    type: Literal["ip", "integer", "string", "enum"] | str
    ui_control: Literal["input", "number", "select", "multi_input"] | str
    multiple: bool
    value_source: Literal["manual", "reference"] | str

    # Дополнительные поля (зависимые от ui_control)
    min: Optional[int] = None
    max: Optional[int] = None
    reference: Optional[str] = None
    reference_description: Optional[str] = None
    match_mode: Optional[Literal["exact", "prefix", "contains"]] = None

    # Пример
    example: Optional[Union[str, int, float, bool, List[str]]] = Field(
        default=None,
        description="Пример заполнения поля"
    )


class MatchFieldResponseSchema(BaseModel):
    items: list[MatchFieldSchema]
    count: int
    frontend_rules: "FrontendRulesForMatchFields"


class FrontendRulesForMatchFields(BaseModel):
    select: str
    input: str
    number: str
    multi_input: str

class SuppressionRuleStatusSchema(BaseModel):
    enabled: bool = Field(..., description="Статус активности правила")


class SuppressionRuleTestSchema(BaseModel):
    rule: SuppressionRequestPostSchema = Field(..., description="Проверяемое правило подавления")
    incident: IncidentTestSchema = Field(..., description="Инцидент, на котором проверяется правило")


# ---------- справочник полей блока action (/reference/suppression-action-fields) ----------

class ActionFieldValueSchema(BaseModel):
    value: str
    label: str


class ActionFieldSchema(BaseModel):
    field: str = Field(..., description="Имя поля в блоке action")
    path: str = Field(..., description="Путь поля в теле правила, например action.severity")
    label: str
    description: str
    type: Literal["enum", "number", "boolean", "string"] | str
    ui_control: Literal["select", "number", "boolean", "input"] | str
    multiple: bool
    required: bool
    default: Optional[Union[bool, int, float, str]] = Field(default=None, description="Значение по умолчанию")
    values: Optional[list[ActionFieldValueSchema]] = Field(default=None, description="Варианты для select (если заданы)")
    reference: Optional[str] = Field(default=None, description="Endpoint со значениями для select")
    reference_description: Optional[str] = None
    min: Optional[int] = None
    max: Optional[int] = None


class FrontendRulesForActionFields(BaseModel):
    select: str
    number: str
    boolean: str
    input: str


class ActionFieldResponseSchema(BaseModel):
    items: list[ActionFieldSchema]
    count: int
    frontend_rules: FrontendRulesForActionFields
