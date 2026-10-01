from typing import Literal, Optional, Any
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class WazuhAgentSchema(BaseModel):
    model_config = ConfigDict(extra="allow")

    ip: str | None = None
    id: str | None = None
    name: str | None = None
    version: str | None = None
    ephemeral_id: str | None = None
    type: str | None = None


class WazuhDecoderSchema(BaseModel):
    model_config = ConfigDict(extra="allow")

    name: str | None = None


class WazuhEcsSchema(BaseModel):
    model_config = ConfigDict(extra="allow")

    version: str | None = None


class WazuhOsSchema(BaseModel):
    model_config = ConfigDict(extra="allow")

    codename: str | None = None
    type: str | None = None
    platform: str | None = None
    version: str | None = None
    family: str | None = None
    name: str | None = None
    kernel: str | None = None


class WazuhHostSchema(BaseModel):
    model_config = ConfigDict(extra="allow")

    os: WazuhOsSchema | None = None
    id: str | None = None
    containerized: bool | None = None
    name: str | None = None
    ip: list[str] = Field(default_factory=[])
    mac: list[str] = Field(default_factory=[])
    hostname: str | None = None
    architecture: str | None = None


class WazuhLogFileSchema(BaseModel):
    model_config = ConfigDict(extra="allow")

    path: str | None = None
    device_id: str | None = None
    inode: int | None = None


class WazuhLogSchema(BaseModel):
    model_config = ConfigDict(extra="allow")

    offset: int | None = None
    file: WazuhLogFileSchema | None = None


class WazuhManagerSchema(BaseModel):
    model_config = ConfigDict(extra="allow")

    name: str | None = None


class WazuhPredecoderSchema(BaseModel):
    model_config = ConfigDict(extra="allow")

    program_name: str | None = None
    timestamp: str | None = None
    hostname: str | None = None


class WazuhInputSchema(BaseModel):
    model_config = ConfigDict(extra="allow")

    type: str | None = None


class WazuhEventSchema(BaseModel):
    """
    Одно событие из Wazuh / Elasticsearch.
    """

    model_config = ConfigDict(extra="allow")

    timestamp: datetime | None = None
    at_timestamp: datetime | None = Field(
        default=None,
        alias="@timestamp",
    )

    agent: WazuhAgentSchema | None = None
    decoder: WazuhDecoderSchema | None = None
    ecs: WazuhEcsSchema | None = None
    host: WazuhHostSchema | None = None
    log: WazuhLogSchema | None = None
    location: str | None = None
    manager: WazuhManagerSchema | None = None
    full_log: str | None = None
    id: str | None = None
    predecoder: WazuhPredecoderSchema | None = None
    input: WazuhInputSchema | None = None

    elastic_index: str | None = Field(
        default=None,
        alias="_elastic_index",
    )

    elastic_id: str | None = Field(
        default=None,
        alias="_elastic_id",
    )


class IncidentEventResponseSchema(BaseModel):
    """
    Ответ API:
    {
        incident_id,
        organization_id,
        attack_type,
        observer_host,
        items,
        total,
        page,
        size,
        returned,
        missing,
        missing_count
    }
    """

    model_config = ConfigDict(extra="allow")

    incident_id: str
    organization_id: str
    attack_type: str
    observer_host: str

    items: list[WazuhEventSchema] = Field(
        default_factory=[]
    )

    total: int = Field(ge=0)
    page: int = Field(ge=1)
    size: int = Field(ge=1)
    returned: int = Field(ge=0)

    missing: list[Any] = Field(
        default_factory=[]
    )

    missing_count: int = Field(ge=0)

AnalystStatus  = Literal["new", "in_review", "confirmed", "false_positive", "closed"]


class UpdateAnalystStatusSchema(BaseModel):
    analyst_status: AnalystStatus

class IncidentParams(BaseModel):
    page: int
    size: int
    organization_id: Optional[str] = None
    from_time: Optional[str] = None
    to_time: Optional[str] = None
    source_ip: Optional[str] = None
    destination_ip: Optional[str] = None
    host: Optional[str] = None
    user: Optional[str] = None
    attack_type: Optional[str] = None
    severity: Optional[str] = None
    analyst_status: Optional[AnalystStatus ] = None
    decision: Optional[str] = None
    action: Optional[str] = None
    priority: Optional[int] = None
    suppressed: Optional[bool] = None
    mitre_id: Optional[str] = None
    campaign_id: Optional[str] = None
    incident_id: Optional[str] = None
    risk_score_min: Optional[float] = None
    risk_score_max: Optional[float] = None
    detection_category: Optional[str] = None
    source_id: Optional[str] = None
    text: Optional[str] = None


class IncidentLite(BaseModel):
    incident_id: str
    start_time: str
    end_time: Optional[str] = None
    severity: Literal["low", "medium", "high", "critical"]
    risk_score: float  # или int, в зависимости от бизнес-логики
    priority: int
    analyst_status: Literal[
        "new", "in_review", "confirmed", "false_positive", "closed"
    ]
    organization_id: str
    attack_type: str
    source_ip: Optional[str] = None
    source_user: Optional[str] = None
    observer_host: str
    destination_ip: Optional[str] = None
    destination_host: Optional[str] = None
    decision: Literal["decision ", "malicious"]  # сохранен опечаточный пробел из TypeScript
    action: Literal["monitor", "block", "investigate"]
    suppressed: bool
    event_count: int
    scenario_count: int
    raw_event_count: int
    ioc_match_count: int


class IncidentApiResponse(BaseModel):
    items: list[IncidentLite]
    total: int
    page: int
    size: int


class ElasticEventRef(BaseModel):
    index: str
    id: str


class ScoreBreakdown(BaseModel):
    mitre: str
    technique: str
    base: int
    final: int


class Incident(BaseModel):
    # Метаданные записи и временные метки
    timestamp: datetime = Field(..., alias="@timestamp")
    incident_id: str
    organization_id: str | None = None
    start_time: datetime | None = None
    end_time: datetime | None = None
    duration_seconds: float

    # Классификация MITRE ATT&CK и атаки
    attack_type: str
    mitre_ids: list[str]
    tactics: list[str]
    kill_chain: str
    attack_id: str
    campaign_id: str
    scenario_ids: list[str]
    risk_score: int
    severity: str
    decision: str
    action: str
    priority: int
    score_breakdown: ScoreBreakdown

    # Сетевые параметры и хосты
    source_ip: Optional[str] = None
    source_ips: list[str] = list
    source_users: list[str] = list
    source_hosts: list[str] = list
    observer_host: str
    destination_ip: str
    destination_ips: list[str]
    destination_host: str
    destination_hosts: list[str]
    target_ports: list[int] = list
    target_users: list[str] = list

    # Метрики событий
    event_count: int
    micro_incidents: int
    unique_sources: int
    has_success: bool
    session_key: str

    # Источники логов и ссылки
    elastic_event_refs: list[ElasticEventRef]
    log_source_types: list[str] = list
    szi_sources: list[str] = list
    product_names: list[str] = list
    vendor_names: list[str] = list

    # Payload и HTTP атрибуты
    payloads: list[Any] = list
    payload_type: Optional[str] = None
    payload_indicators: list[Any] = list
    request_uris: list[str] = list
    urls: list[str] = list
    http_methods: list[str] = list
    http_statuses: list[int] = list
    user_agents: list[str] = list

    # Детекция и правила
    event_actions: list[str] = list
    signatures: list[str] = list
    signature_ids: list[str] = list
    attack_names: list[str] = list
    detection_rule_ids: list[str] = list
    detection_rule_descriptions: list[str] = list
    detection_categories: list[str] = list
    detection_confidences: list[float] = list
    severity_hints: list[str] = list
    scenario_type: Optional[str] = None
    recommendations: list[str] = list

    # Системные и лог-атрибуты (Windows / Linux)
    event_codes: list[int] = list
    winlog_channels: list[str] = list
    computer_names: list[str] = list
    process_names: list[str] = list
    process_paths: list[str] = list
    process_command_lines: list[str] = list
    parent_process_names: list[str] = list
    parent_process_paths: list[str] = list
    parent_process_command_lines: list[str] = list
    file_paths: list[str] = list
    registry_keys: list[str] = list
    service_names: list[str] = list
    task_names: list[str] = list

    # Подавление (Suppression)
    suppressed: bool
    suppression_mode: Optional[str] = None
    suppression_rule: Optional[str] = None
    suppression_reason: Optional[str] = None

    # Описание и аналитика
    explanation: list[str]
    ai_analysis: Optional[str] = None
    extra: dict[str, Any] = dict

    # Служебные Elastic полей и статус
    elastic_index: str = Field(..., alias="_elastic_index")
    elastic_id: str = Field(..., alias="_elastic_id")
    analyst_status: str

    asset_id: str | None = None
    asset_hostname: str | None = None
    asset_type: str | None = None
    asset_criticality: str | None = None
    asset_tags: list[str] | None = None
    source_ids: list[str] | None = None


class MitreInfo(BaseModel):
    ids: list[str]
    tactics: list[str]
    techniques: list[str] = list


class IncidentLinks(BaseModel):
    raw_events: str
    scenario: str | None = None
    case: str | None = None


class IncidentSchema(BaseModel):
    incident: Incident
    scenario_ids: list[str] = list
    related_scenarios: list[Any] = list
    raw_event_count: int
    ioc_match_count: int
    ioc_matches: list[str] = list
    mitre: MitreInfo
    links: IncidentLinks