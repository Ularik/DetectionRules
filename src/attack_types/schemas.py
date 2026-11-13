from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime


class AttackSchema(BaseModel):
    label: str
    value: str

class AttackApiResponseSchema(BaseModel):
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
