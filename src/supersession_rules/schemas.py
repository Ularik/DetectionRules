from datetime import datetime
from typing import List, Optional, Literal, Union
from pydantic import BaseModel, Field, model_validator


class SuppressionMatchSchema(BaseModel):
    source_ip: Optional[str] = Field(default=None, description="IP-адрес источника")
    destination_ip: Optional[str] = Field(default=None, description="IP-адрес назначения")
    dst_port: Optional[int] = Field(default=None, description="Порт назначения")
    observer_host: Optional[str] = Field(default=None, description="Хост-наблюдатель")
    attack_type: Optional[str] = Field(default=None, description="Тип атаки")
    detection_rule_id: Optional[str] = Field(default=None, description="ID правила детектирования")
    category: Optional[str] = Field(default=None, description="Категория")
    paths: List[str] = Field(default_factory=[], description="Список путей")
    path_prefixes: List[str] = Field(default_factory=[], description="Префиксы путей")
    contains: List[str] = Field(default_factory=[], description="Содержимое")

    @model_validator(mode="after")
    def check_at_least_one_field_present(self) -> "SuppressionMatchSchema":
        has_data = any(
            value is not None and value != []
            for value in self.model_dump().values()
        )
        if not has_data:
            raise ValueError("Хотя бы одно критерий совпадения (поле) должно быть заполнено")
        return self


class SuppressionMatchUpdateSchema(BaseModel):
    source_ip: Optional[str] = Field(default=None, description="IP-адрес источника")
    attack_type: Optional[str] = Field(default=None, description="Тип атаки")


class SuppressionActionSchema(BaseModel):
    mode: str | None = Field(default='supress', description="Режим подавления")
    attack_type: Optional[str] = Field(default=None, description="Переопределение типа атаки")
    decision: str | None = Field(default=None, description="Решение")
    severity: str = Field(..., description="Уровень суровости")
    risk_score: int | None = Field(default=0, description="Оценка риска")
    action: str | None = Field(default=None, description="Выполняемое действие")
    suppressed: bool = Field(..., description="Флаг подавления")
    suppression_reason: str | None = Field(default=None, description="Причина подавления")


class SuppressionRuleSchema(BaseModel):
    suppression_id: str = Field(..., description="Уникальный идентификатор правила подавления")
    enabled: bool = Field(..., description="Статус активности правила")
    description: str = Field(..., description="Описание правила")
    reason: str = Field(..., description="Причина создания правила")
    match: SuppressionMatchSchema = Field(..., description="Условия срабатывания правила")
    action_details: SuppressionActionSchema = Field(..., alias="action", description="Действия при срабатывании")
    tags: List[str] = Field(default_factory=[], description="Теги")
    created_at: Optional[datetime] = Field(default=None, description="Дата и время создания")
    updated_at: Optional[datetime] = Field(default=None, description="Дата и время обновления")
    created_by: str | None = Field(default=None, description="Автор создания")
    updated_by: str | None = Field(default=None, description="Автор последнего обновления")

    class Config:
        populate_by_name = True


class SuppressionRuleUpdateSchema(BaseModel):
    description: str = Field(
        ...,
        description="Краткое описание правила"
    )
    reason: str = Field(
        ...,
        description="Причина создания правила"
    )
    match: SuppressionMatchUpdateSchema = Field(
        ...,
        description="Условия совпадения"
    )
    action: str = Field(
        ...,
        description="Действие при совпадении (например, ignore, block)"
    )
    suppressed: bool = Field(
        ...,
        description="Статус подавления"
    )
    suppression_reason: str = Field(
        ...,
        description="Детальная причина подавления"
    )
    tags: List[str] = Field(
        default_factory=[],
        description="Список тегов"
    )


class SuppressionRuleCreateUpdateResultSchema(BaseModel):
    success: bool
    rule: SuppressionRuleSchema


class SuppressionRequestPostSchema(BaseModel):
    enabled: bool = Field(..., description="Статус активности правила")
    description: str | None = Field(default=None, description="Описание правила")
    reason: str | None = Field(default=None, description="Причина создания правила")
    match: SuppressionMatchSchema = Field(..., description="Условия срабатывания правила")
    action_details: SuppressionActionSchema | None = Field(default=None, alias="action", description="Действия при срабатывании")
    tags: List[str] = Field(default_factory=[], description="Теги")


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