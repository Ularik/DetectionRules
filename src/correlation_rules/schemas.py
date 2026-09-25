from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field, FieldValidationInfo, ConfigDict, field_validator
import re

# ----------------------------------------------------------------------
# Base Model (общие поля для чтения/записи)
# ----------------------------------------------------------------------
class CorrelationRuleRequestCreateUpdateSchema(BaseModel):
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
        examples=["Обновленная корреляция SSH brute force и успешного входа"],
    )
    window_seconds: int = Field(
        ...,
        gt=0,
        description="Максимальное временное окно между инцидентами в секундах",
        examples=[1800],
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
    min_unique_categories: int | None = Field(
        default=None,
        ge=1,
        description="Минимальное число уникальных категорий для срабатывания",
        examples=[2],
    )
    severity: str | None = None
    confidence: int = Field(
        default=0,
        ge=0,
        le=100,
        description="Уверенность правила (0–100)",
        examples=[90],
    )
    recommendations: Optional[List[str]] = Field(
        default_factory=[],
        description="Рекомендации аналитику",
        examples=[["Проверить успешные входы после серии неуспешных попыток"]],
    )
    tags: Optional[List[str]] = Field(
        default_factory=[],
        description="Теги правила",
        examples=[["ssh", "bruteforce"]],
    )


class CorrelationRuleCreateSchema(CorrelationRuleRequestCreateUpdateSchema):
    created_by: str
    updated_by: str


class CorrelationRuleDBSchema(CorrelationRuleCreateSchema):
    id: int
    correlation_id: str | None = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

    @field_validator("created_at", "updated_at", mode="before")
    @classmethod
    def fix_pg_timezone(cls, v):
        if isinstance(v, str):
            # Если смещение указано без минут, например +05 или -03, дописываем :00
            v = re.sub(r"([+-]\d{2})$", r"\1:00", v)
        return v


class CorrelationRuleESSchema(CorrelationRuleRequestCreateUpdateSchema):
    correlation_id: str
    created_at: str
    updated_at: str
    created_by: str | None = None
    updated_by: str | None = None

class CorrelationRuleCreateFromOldSchema(CorrelationRuleESSchema):
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(extra="ignore")


class CorrelationRuleUpdateESSchema(CorrelationRuleRequestCreateUpdateSchema):
    updated_by: str


class CorrelationApiResponseSchema(BaseModel):
    status: str
    rule: CorrelationRuleESSchema