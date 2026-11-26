from typing import Any, List, Optional
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict, field_validator
import re

from src.incidents.schemas import IncidentTestSchema
from src.rules.models import SeverityHintEnum


# Пример правила корреляции для OpenAPI (формат ответа внешнего API)
CORRELATION_RULE_ES_EXAMPLE: dict = {
    "correlation_id": "CORR-0031399A",
    "name": "SSH brute force и успешный вход",
    "enabled": True,
    "scenario_type": "ssh_bruteforce_chain",
    "description": "Корреляция SSH brute force и последующего успешного входа",
    "window_seconds": 1800,
    "sequence": ["ssh_bruteforce", "successful_login_after_bruteforce"],
    "group_by": ["source_ip"],
    "min_unique_categories": 2,
    "severity": "high",
    "confidence": 90,
    "recommendations": ["Проверить успешные входы после серии неуспешных попыток"],
    "tags": ["ssh", "bruteforce"],
    "mitre_ids": ["T1110"],
    "created_at": "2026-09-25T08:41:04.283735+00:00",
    "updated_at": "2026-09-25T09:51:46.650107+00:00",
    "created_by": "ular",
    "updated_by": "analyst1",
}


# ----------------------------------------------------------------------
# Base Model — нестрогая версия для чтения (ответы внешнего API, PG),
# где у старых правил часть полей может отсутствовать
# ----------------------------------------------------------------------
class CorrelationRuleBaseSchema(BaseModel):
    enabled: bool = Field(
        default=True,
        description="Включено ли правило",
    )
    scenario_type: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Тип сценария, который формируется этим правилом",
        examples=["ssh_bruteforce_chain"],
    )
    description: Optional[str] = Field(
        default=None,
        description="Описание логики правила",
        examples=["Корреляция SSH brute force и последующего успешного входа"],
    )
    window_seconds: int = Field(
        ...,
        gt=0,
        description="Максимальное временное окно между инцидентами в секундах",
        examples=[1800],
    )
    sequence: List[str] = Field(
        default_factory=list,
        description="Последовательность типов инцидентов/атак, которые должны связаться",
        examples=[["ssh_bruteforce", "successful_login_after_bruteforce"]],
    )
    group_by: List[str] = Field(
        default_factory=list,
        description="Поля, по которым инциденты считаются связанными",
        examples=[["source_ip"]],
    )
    min_unique_categories: int | None = Field(
        default=None,
        ge=1,
        description="Минимальное число уникальных категорий для срабатывания",
        examples=[2],
    )
    severity: SeverityHintEnum | None = Field(
        default=None,
        description="Критичность формируемого сценария",
        examples=["high"],
    )
    confidence: int = Field(
        default=0,
        ge=0,
        le=100,
        description="Уверенность правила (0–100)",
        examples=[90],
    )
    recommendations: List[str] = Field(
        default_factory=list,
        description="Рекомендации аналитику",
        examples=[["Проверить успешные входы после серии неуспешных попыток"]],
    )
    tags: List[str] = Field(
        default_factory=list,
        description="Теги правила",
        examples=[["ssh", "bruteforce"]],
    )

    @field_validator("recommendations", "tags", "sequence", "group_by", mode="before")
    @classmethod
    def none_to_list(cls, v):
        return [] if v is None else v


MITRE_IDS_DESCRIPTION = "Техники MITRE ATT&CK (значения — из GET /api/mitre/mitre)"
NAME_DESCRIPTION = "Отображаемое название правила корреляции (не correlation_id)"


# ----------------------------------------------------------------------
# Правило в теле POST /test — CorrelationRuleTestData из API движка (без mitre_ids)
# ----------------------------------------------------------------------
class CorrelationRuleTestRuleSchema(CorrelationRuleBaseSchema):
    """Обязательны scenario_type, description, window_seconds, severity, confidence (как в API движка).
    sequence и group_by движок формально не требует, но без них правило ничего не коррелирует,
    поэтому проверяем, что они не пустые."""
    description: str = Field(
        ...,
        min_length=1,
        description="Описание логики правила",
        examples=["Корреляция SSH brute force и последующего успешного входа"],
    )
    sequence: List[str] = Field(
        ...,
        min_length=1,
        description="Последовательность типов инцидентов/атак, которые должны связаться",
        examples=[["ssh_bruteforce", "successful_login_after_bruteforce"]],
    )
    group_by: List[str] = Field(
        ...,
        min_length=1,
        description="Поля, по которым инциденты считаются связанными",
        examples=[["source_ip"]],
    )
    severity: SeverityHintEnum = Field(
        ...,
        description="Критичность формируемого сценария",
        examples=["high"],
    )
    confidence: int = Field(
        ...,
        ge=0,
        le=100,
        description="Уверенность правила (0–100)",
        examples=[90],
    )


# ----------------------------------------------------------------------
# Тело запроса на создание/изменение — CorrelationRuleCreate/Update из API движка
# ----------------------------------------------------------------------
class CorrelationRuleRequestCreateUpdateSchema(CorrelationRuleTestRuleSchema):
    name: Optional[str] = Field(
        default=None,
        max_length=200,
        description=NAME_DESCRIPTION,
        examples=["SSH brute force и успешный вход"],
    )
    mitre_ids: List[str] = Field(
        default_factory=list,
        description=MITRE_IDS_DESCRIPTION,
        examples=[["T1110"]],
    )

    @field_validator("mitre_ids", mode="before")
    @classmethod
    def mitre_none_to_list(cls, v):
        return [] if v is None else v


class CorrelationRuleCreateSchema(CorrelationRuleRequestCreateUpdateSchema):
    created_by: str
    updated_by: str


class CorrelationRuleDBSchema(CorrelationRuleBaseSchema):
    id: int
    correlation_id: str | None = None
    name: Optional[str] = Field(default=None, description=NAME_DESCRIPTION)
    mitre_ids: List[str] = Field(default_factory=list, description=MITRE_IDS_DESCRIPTION)
    created_by: str
    updated_by: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

    @field_validator("mitre_ids", mode="before")
    @classmethod
    def mitre_none_to_list(cls, v):
        return [] if v is None else v

    @field_validator("created_at", "updated_at", mode="before")
    @classmethod
    def fix_pg_timezone(cls, v):
        if isinstance(v, str):
            # Если смещение указано без минут, например +05 или -03, дописываем :00
            v = re.sub(r"([+-]\d{2})$", r"\1:00", v)
        return v


class CorrelationRuleESSchema(CorrelationRuleBaseSchema):
    """Правило корреляции в том виде, в каком его отдаёт внешний API"""
    correlation_id: str = Field(description="Идентификатор правила корреляции", examples=["CORR-0031399A"])
    name: Optional[str] = Field(default=None, description=NAME_DESCRIPTION)
    mitre_ids: List[str] = Field(default_factory=list, description=MITRE_IDS_DESCRIPTION, examples=[["T1110"]])

    @field_validator("mitre_ids", mode="before")
    @classmethod
    def mitre_none_to_list(cls, v):
        return [] if v is None else v
    created_at: str
    updated_at: str
    created_by: str | None = None
    updated_by: str | None = None

    model_config = ConfigDict(json_schema_extra={"examples": [CORRELATION_RULE_ES_EXAMPLE]})


class CorrelationRuleCreateFromOldSchema(CorrelationRuleESSchema):
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(extra="ignore")


class CorrelationRuleUpdateESSchema(CorrelationRuleRequestCreateUpdateSchema):
    updated_by: str


class CorrelationApiResponseSchema(BaseModel):
    """Ответ внешнего API на создание/изменение/смену статуса: {status, rule, similar_rule_ids?, warnings?}"""
    status: str
    rule: CorrelationRuleESSchema
    similar_rule_ids: List[str] = Field(default_factory=list, description="ID похожих правил (если движок их нашёл)")
    warnings: List[Any] = Field(default_factory=list, description="Предупреждения движка")


class CorrelationRuleStatusSchema(BaseModel):
    enabled: bool = Field(..., description="Статус активности правила")


class CorrelationRuleDeleteResponseSchema(BaseModel):
    """Результат удаления правила корреляции"""
    correlation_id: str
    deleted: bool = True

    model_config = ConfigDict(json_schema_extra={
        "examples": [{"correlation_id": "CORR-0031399A", "deleted": True}]
    })


class CorrelationRuleTestSchema(BaseModel):
    rule: CorrelationRuleTestRuleSchema = Field(..., description="Проверяемое правило корреляции")
    incidents: List[IncidentTestSchema] = Field(..., description="Инциденты, на которых проверяется правило")


class CorrelationRuleTestResponseSchema(BaseModel):
    """Результат тестового прогона правила корреляции (ответ внешнего API)"""
    matched: bool = Field(description="Связались ли инциденты по правилу")
    scenario_type: str | None = Field(default=None, description="Сценарий, который был бы создан (если matched)")
    severity: str | None = None
    confidence: int | None = None
    recommendations: List[str] = Field(default_factory=list)

    model_config = ConfigDict(extra="allow", json_schema_extra={
        "examples": [
            {
                "matched": True,
                "scenario_type": "ssh_bruteforce_chain",
                "severity": "high",
                "confidence": 90,
                "recommendations": ["Проверить успешные входы после серии неуспешных попыток"],
            },
            {"matched": False, "scenario_type": None, "severity": None, "confidence": None, "recommendations": []},
        ]
    })


# ----------------------------------------------------------------------
# Справочники для формы правила корреляции
# ----------------------------------------------------------------------
class SequenceItemSchema(BaseModel):
    value: str
    label: str

    model_config = ConfigDict(json_schema_extra={
        "examples": [{"value": "ssh_bruteforce", "label": "ssh_bruteforce"}]
    })


class SequenceSchema(BaseModel):
    items: list[SequenceItemSchema]


class CorrelationGroupByFieldsSchema(BaseModel):
    value: str
    label: str
    description: str


class GroupByResponseSchema(BaseModel):
    items: list[CorrelationGroupByFieldsSchema]
    count: int | None = None

    model_config = ConfigDict(json_schema_extra={
        "examples": [{
            "items": [
                {"value": "source_ip", "label": "Source IP", "description": "Связывать инциденты по IP-адресу источника."},
                {"value": "source_user", "label": "Source user", "description": "Связывать инциденты по учётной записи источника."},
            ],
            "count": 2,
        }]
    })


class ScenarioTypesResponseSchema(BaseModel):
    """Справочник значений поля scenario_type (прокси /reference/scenario-types)"""
    items: list[SequenceItemSchema]
    count: int | None = None

    model_config = ConfigDict(json_schema_extra={
        "examples": [{
            "items": [
                {"value": "ssh_bruteforce_chain", "label": "SSH Brute Force Chain"},
                {"value": "other", "label": "Другой тип"},
            ],
            "count": 2,
        }]
    })


class ScenarioTypeCreateSchema(BaseModel):
    """Тело POST /reference/scenario-types (ScenarioTypeCreate движка)"""
    value: str = Field(..., min_length=1, description="Значение scenario_type, например credential_access_only")
    label: str = Field(..., min_length=1, description="Отображаемое название")
    description: str = Field("", description="Описание типа сценария")

    model_config = ConfigDict(json_schema_extra={
        "examples": [{"value": "credential_access_only", "label": "Credential Access", "description": ""}]
    })


class ScenarioTypeCreateResponseSchema(BaseModel):
    """Ответ POST /reference/scenario-types движка"""
    success: bool
    scenario_type: ScenarioTypeCreateSchema = Field(..., description="Добавленный тип сценария")


class ScenarioTypeUpdateSchema(BaseModel):
    """Тело PUT /reference/scenario-types/{value} (ScenarioTypeUpdate движка); value меняется только через новое значение"""
    label: str = Field(..., min_length=1, description="Отображаемое название")
    description: str = Field("", description="Описание типа сценария")


class ScenarioTypeDeleteResponseSchema(BaseModel):
    """Ответ DELETE /reference/scenario-types/{value} движка"""
    success: bool
    deleted: str = Field(..., description="Удалённое значение scenario_type")
