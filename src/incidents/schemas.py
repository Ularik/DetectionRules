from typing import Literal, Optional, Any
from datetime import datetime
from typing import Any
from pydantic import BaseModel, ConfigDict, Field

from src.events.schema import WazuhEventSchema


class IncidentLiteSchema(BaseModel):
    incident_id: str = Field(description="ID Incident")
    start_time: datetime = Field(description="Начало")
    end_time: datetime = Field(description="Окончание")
    severity: str = Field(description="Критичность")
    risk_score: int = Field(description="Risk score")
    priority: int = Field(description="Приоритет")
    attack_type: str = Field(description="Тип активности")
    source_ip: Optional[str] = Field(default=None, description="Source IP")
    source_user: Optional[str] = Field(default=None, description="Source user")
    observer_host: Optional[str] = Field(default=None, description="Observer host")
    destination_ip: Optional[str] = Field(default=None, description="Destination IP")
    destination_host: Optional[str] = Field(default=None, description="Destination host")
    decision: str = Field(description="Decision")
    action: str = Field(description="Action")
    organization_id: str | None = Field(default=None, description="Организация")
    event_count: int = Field(description="Количество событий")

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True
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
    organization_id: str | None = None
    attack_type: str
    observer_host: str

    items: list[WazuhEventSchema] = Field(
        default_factory=list
    )

    total: int = Field(ge=0)
    page: int = Field(ge=1)
    size: int = Field(ge=1)
    returned: int = Field(ge=0)

    missing: list[Any] = Field(
        default_factory=list
    )

    missing_count: int = Field(ge=0)

AnalystStatus  = Literal["new", "in_review", "confirmed", "false_positive", "closed"]


class UpdateAnalystStatusSchema(BaseModel):
    analyst_status: AnalystStatus

class IncidentParams(BaseModel):
    page: Optional[int] = None
    size: Optional[int] = None
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
    """Элемент списка /hunting/incidents (облегчённая запись, не полный Incident)."""
    model_config = ConfigDict(extra="allow")

    incident_id: str
    start_time: datetime
    end_time: Optional[datetime] = None
    severity: Optional[str] = None
    risk_score: Optional[float] = None
    priority: Optional[int] = None
    analyst_status: Optional[str] = None
    organization_id: Optional[str] = None
    attack_type: Optional[str] = None
    source_ip: Optional[str] = None
    source_user: Optional[str] = None
    observer_host: Optional[str] = None
    destination_ip: Optional[str] = None
    destination_host: Optional[str] = None
    decision: Optional[str] = None
    action: Optional[str] = None
    suppressed: Optional[bool] = None
    event_count: int = 0
    scenario_count: int = 0
    raw_event_count: int = 0
    ioc_match_count: int = 0


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
    duration_seconds: float | None = None

    # Классификация MITRE ATT&CK и атаки
    attack_type: str | None = None
    mitre_ids: list[str] = Field(default_factory=list)
    tactics: list[str] = Field(default_factory=list)
    kill_chain: str | None = None
    attack_id: str | None = None
    campaign_id: str | None = None
    scenario_ids: list[str] = Field(default_factory=list)
    risk_score: int | None = None
    severity: str | None = None
    decision: str | None = None
    action: str | None = None
    priority: int | None = None
    score_breakdown: ScoreBreakdown | None = None

    # Сетевые параметры и хосты
    source_ip: Optional[str] = None
    source_ips: list[str] = Field(default_factory=list)
    source_users: list[str] = Field(default_factory=list)
    source_hosts: list[str] = Field(default_factory=list)
    observer_host: str | None = None
    destination_ip: str | None = None
    destination_ips: list[str] = Field(default_factory=list)
    destination_host: str | None = None
    destination_hosts: list[str] = Field(default_factory=list)
    target_ports: list[int] = Field(default_factory=list)
    target_users: list[str] = Field(default_factory=list)

    # Метрики событий
    event_count: int = 0
    micro_incidents: int | None = None
    unique_sources: int | None = None
    has_success: bool | None = None
    session_key: str | None = None

    # Источники логов и ссылки
    elastic_event_refs: list[ElasticEventRef] = Field(default_factory=list)
    log_source_types: list[str] = Field(default_factory=list)
    szi_sources: list[str] = Field(default_factory=list)
    product_names: list[str] = Field(default_factory=list)
    vendor_names: list[str] = Field(default_factory=list)

    # Payload и HTTP атрибуты
    payloads: list[Any] = Field(default_factory=list)
    payload_type: Optional[str] = None
    payload_indicators: list[Any] = Field(default_factory=list)
    request_uris: list[str] = Field(default_factory=list)
    urls: list[str] = Field(default_factory=list)
    http_methods: list[str] = Field(default_factory=list)
    http_statuses: list[int] = Field(default_factory=list)
    user_agents: list[str] = Field(default_factory=list)

    # Детекция и правила
    event_actions: list[str] = Field(default_factory=list)
    signatures: list[str] = Field(default_factory=list)
    signature_ids: list[str] = Field(default_factory=list)
    attack_names: list[str] = Field(default_factory=list)
    detection_rule_ids: list[str] = Field(default_factory=list)
    detection_rule_descriptions: list[str] = Field(default_factory=list)
    detection_categories: list[str] = Field(default_factory=list)
    detection_confidences: list[float] = Field(default_factory=list)
    severity_hints: list[str] = Field(default_factory=list)
    scenario_type: Optional[str] = None
    recommendations: list[str] = Field(default_factory=list)

    # Системные и лог-атрибуты (Windows / Linux)
    event_codes: list[int] = Field(default_factory=list)
    winlog_channels: list[str] = Field(default_factory=list)
    computer_names: list[str] = Field(default_factory=list)
    process_names: list[str] = Field(default_factory=list)
    process_paths: list[str] = Field(default_factory=list)
    process_command_lines: list[str] = Field(default_factory=list)
    parent_process_names: list[str] = Field(default_factory=list)
    parent_process_paths: list[str] = Field(default_factory=list)
    parent_process_command_lines: list[str] = Field(default_factory=list)
    file_paths: list[str] = Field(default_factory=list)
    registry_keys: list[str] = Field(default_factory=list)
    service_names: list[str] = Field(default_factory=list)
    task_names: list[str] = Field(default_factory=list)

    # Подавление (Suppression)
    suppressed: bool = False
    suppression_mode: Optional[str] = None
    suppression_rule: Optional[str] = None
    suppression_reason: Optional[str] = None

    # Описание и аналитика
    explanation: list[str] = Field(default_factory=list)
    ai_analysis: Optional[str] = None
    extra: dict[str, Any] = Field(default_factory=dict)

    # Служебные Elastic полей и статус
    elastic_index: str = Field(..., alias="_elastic_index")
    elastic_id: str = Field(..., alias="_elastic_id")
    analyst_status: str | None = None

    asset_id: str | None = None
    asset_hostname: str | None = None
    asset_type: str | None = None
    asset_criticality: str | None = None
    asset_tags: list[str] | None = None
    source_ids: list[str] | None = None


class MitreInfo(BaseModel):
    ids: list[str]
    tactics: list[str]
    techniques: list[str] = Field(default_factory=list)


class IncidentLinks(BaseModel):
    raw_events: str
    scenario: str | None = None
    case: str | None = None


class IncidentSchema(BaseModel):
    incident: Optional[Incident] = None
    scenario_ids: list[str] = Field(default_factory=list)
    related_scenarios: list[Any] = Field(default_factory=list)
    raw_event_count: int
    ioc_match_count: int
    ioc_matches: list[str] = Field(default_factory=list)
    mitre: MitreInfo
    links: IncidentLinks


class IncidentTestSchema(BaseModel):
    """Инцидент для тестирования правил подавления/корреляции.

    Описаны основные поля схемы Incident внешнего API, остальные поля
    (их около сотни) принимаются как есть и передаются без изменений.
    """
    model_config = ConfigDict(extra="allow")

    incident_id: str = Field(..., description="Идентификатор инцидента")
    organization_id: str | None = Field(default=None, description="Идентификатор организации")
    attack_type: str = Field(default="unknown", description="Тип атаки")
    scenario_type: str | None = Field(default=None, description="Тип сценария")
    source_ip: str | None = Field(default=None, description="IP-адрес источника")
    destination_ip: str | None = Field(default=None, description="IP-адрес назначения")
    observer_host: str | None = Field(default=None, description="Хост-наблюдатель")
    target_ports: list[Any] = Field(default_factory=list, description="Порты назначения")
    request_uris: list[str] = Field(default_factory=list, description="Запрошенные URI")
    detection_rule_ids: list[str] = Field(default_factory=list, description="ID сработавших правил")
    detection_categories: list[str] = Field(default_factory=list, description="Категории детектирования")
    severity: str = Field(default="low", description="Уровень критичности")
    risk_score: float = Field(default=0.0, description="Оценка риска")
    start_time: str | None = Field(default=None, description="Начало инцидента")
    end_time: str | None = Field(default=None, description="Окончание инцидента")


class IncidentArtifactSchema(BaseModel):
    """Технический признак, извлечённый из поля RAW-события."""
    type: str = Field(..., description="Тип артефакта (command, ip, user и т.д.)")
    value: Any = Field(None, description="Значение")
    field: str | None = Field(None, description="Поле RAW-события, из которого взят артефакт")


class IncidentArtifactEventRefSchema(BaseModel):
    index: str = Field(..., description="Индекс Elasticsearch")
    id: str = Field(..., description="Идентификатор документа")


class IncidentArtifactItemSchema(BaseModel):
    """Артефакты одного RAW-события инцидента."""
    event_id: str | None = None
    timestamp: str | None = None
    hostname: str | None = None
    source_id: str | None = None
    source_name: str | None = None
    action: str | None = None
    rule_id: str | None = None
    rule_description: str | None = None
    rule_level: int | None = None
    mitre_ids: list[str] = Field(default_factory=list)
    artifacts: list[IncidentArtifactSchema] = Field(default_factory=list)
    artifact_count: int = 0
    event_ref: IncidentArtifactEventRefSchema | None = None
    raw_url: str | None = Field(None, description="Путь к RAW-событию во внешнем API")


class IncidentArtifactsResponseSchema(BaseModel):
    """Ответ /hunting/incidents/{id}/artifacts; пагинация по исходным событиям."""
    incident_id: str
    organization_id: str | None = None
    items: list[IncidentArtifactItemSchema] = Field(default_factory=list)
    total: int = 0
    page: int = 1
    size: int = 50
    returned: int = 0
    missing: list[Any] = Field(default_factory=list)
    missing_count: int = 0
