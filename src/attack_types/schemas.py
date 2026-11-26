from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime


class AttackSchema(BaseModel):
    """Элемент справочника /reference/attack-types"""
    value: str = Field(..., description="Значение attack_type")
    label: str = Field(..., description="Отображаемое название")
    description: str = Field("", description="Описание типа атаки")
    source: str | None = Field(
        None, description="Происхождение: system — встроенный (изменять и удалять нельзя), custom — добавлен вручную"
    )
    scopes: list[str] = Field(default_factory=list, description="Области применения (web, linux, ...)")
    rule_count: int = Field(0, ge=0, description="Сколько правил обнаружения используют этот тип атаки")

    model_config = ConfigDict(json_schema_extra={"examples": [{
        "value": "web_exploit_attempt", "label": "web_exploit_attempt",
        "description": "Попытка эксплуатации веб-уязвимости", "source": "system", "scopes": ["web"], "rule_count": 9,
    }]})


class AttackApiResponseSchema(BaseModel):
    """Ответ GET /reference/attack-types"""
    items: list[AttackSchema]
    count: int


class AttackGroupsQueryParams(BaseModel):
    organization_id: str | None = None
    from_time: datetime | None = None
    to_time: datetime | None = None
    page: int = Field(default=1, ge=1)
    size: int = Field(default=10, ge=1)


# Ответ /hunting/ip/{source_ip}

class HuntingIpSummarySchema(BaseModel):
    model_config = ConfigDict(extra="allow")

    incident_count: int = 0
    attack_type_count: int = 0
    destination_count: int = 0
    scenario_count: int = 0
    event_count: int = 0


class AttackGroupDestinationSchema(BaseModel):
    model_config = ConfigDict(extra="allow")

    destination_ip: str
    incident_count: int = 0


class AttackGroupSchema(BaseModel):
    """Группа инцидентов по типу атаки"""
    model_config = ConfigDict(extra="allow")

    attack_type: str
    incident_count: int = 0
    event_count: int = 0
    destination_count: int = 0
    first_seen: datetime | None = None
    last_seen: datetime | None = None
    severities: list[str] = Field(default_factory=list)
    mitre_ids: list[str] = Field(default_factory=list)
    tactics: list[str] = Field(default_factory=list)
    destinations: list[AttackGroupDestinationSchema] = Field(default_factory=list)


class HuntingIpDestinationSchema(BaseModel):
    """Атакуемый адрес с агрегатами по нему"""
    model_config = ConfigDict(extra="allow")

    destination_ip: str
    incident_count: int = 0
    event_count: int = 0
    attack_types: list[str] = Field(default_factory=list)
    first_seen: datetime | None = None
    last_seen: datetime | None = None


class HuntingIpIncidentSchema(BaseModel):
    """Облегчённая запись инцидента в ответе hunting по IP"""
    model_config = ConfigDict(extra="allow")

    incident_id: str
    organization_id: str | None = None
    attack_type: str | None = None
    source_ip: str | None = None
    destination_ip: str | None = None
    destination_ips: list[str] = Field(default_factory=list)
    destination_host: str | None = None
    asset_id: str | None = None
    asset_hostname: str | None = None
    asset_type: str | None = None
    asset_criticality: str | None = None
    asset_tags: list[str] = Field(default_factory=list)
    start_time: datetime | None = None
    end_time: datetime | None = None
    severity: str | None = None
    risk_score: float | None = None
    priority: int | None = None
    decision: str | None = None
    action: str | None = None
    event_count: int = 0
    mitre_ids: list[str] = Field(default_factory=list)
    tactics: list[str] = Field(default_factory=list)
    scenario_ids: list[str] = Field(default_factory=list)
    scenario_count: int = 0


class AttackGroupsResponseSchema(BaseModel):
    model_config = ConfigDict(extra="allow")

    source_ip: str
    from_time: datetime | None = None
    to_time: datetime | None = None
    summary: HuntingIpSummarySchema
    attack_groups: list[AttackGroupSchema] = Field(default_factory=list)
    destinations: list[HuntingIpDestinationSchema] = Field(default_factory=list)
    incidents: list[HuntingIpIncidentSchema] = Field(default_factory=list)
    page: int
    size: int


# Запись в справочник /reference/attack-types

class AttackTypeCreateSchema(BaseModel):
    """Тело POST /reference/attack-types (AttackTypeCreate движка)"""
    value: str = Field(..., min_length=1, description="Значение attack_type, например ssh_bruteforce")
    label: str = Field(..., min_length=1, description="Отображаемое название")
    description: str = Field("", description="Описание типа атаки")


class AttackTypeUpdateSchema(BaseModel):
    """Тело PUT /reference/attack-types/{value} (AttackTypeUpdate движка)"""
    label: str = Field(..., min_length=1, description="Отображаемое название")
    description: str = Field("", description="Описание типа атаки")


class AttackTypeResponseSchema(BaseModel):
    """Ответ POST/PUT /reference/attack-types движка"""
    success: bool
    attack_type: AttackTypeCreateSchema


class AttackTypeDeleteResponseSchema(BaseModel):
    """Ответ DELETE /reference/attack-types/{value} движка"""
    success: bool
    deleted: str
