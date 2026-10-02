from datetime import datetime
from src.incidents.schemas import AnalystStatus
from enum import Enum
from typing import Optional, Literal, Any
from pydantic import BaseModel, Field, IPvAnyAddress, ConfigDict
from src.ioc.schemas import IocItemSchema
from src.mitre.schemas import MitreSchema
from src.incidents.schemas import IncidentLiteSchema
from src.events.schema import WazuhEventSchema


class ScenariosEventsApiResponseSchema(BaseModel):
    organization_id: str
    scenario_type: str
    incident_ids: list[str]
    items: list[WazuhEventSchema]
    total: int
    page: int
    size: int
    returned: int
    missing: list[str]
    missing_count: int


class SeverityEnum(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ScenarioEventsParams(BaseModel):
    page: int = Field(default=1)
    size: int = Field(default=10)


class ScenarioQueryParams(BaseModel):
    # Строковые и идентификационные фильтры
    organization_id: Optional[str] = Field(None, description="Фильтр по ID организации")
    scenario_id: Optional[str] = Field(None, description="Фильтр по ID сценария")
    scenario_type: Optional[str] = Field(None, description="Тип сценария")

    # Сетевые фильтры
    source_ip: Optional[IPvAnyAddress] = Field(None, description="IP-адрес источника")
    destination_ip: Optional[IPvAnyAddress] = Field(None, description="IP-адрес назначения")
    host: Optional[str] = Field(None, description="Имя хоста")
    user: Optional[str] = Field(None, description="Имя пользователя")

    # Категории и типы атак
    attack_type: Optional[str] = Field(None, description="Тип атаки")
    detection_category: Optional[str] = Field(None, description="Категория детекта")

    # Enum фильтры
    severity: Optional[SeverityEnum] = Field(None, description="Уровень критичности")
    analyst_status: Optional[AnalystStatus] = Field(None, description="Статус аналитика")
    decision: Optional[Literal["malicious", "suspicious"]] = Field(None, description="Решение по инциденту")
    action: Optional[Literal["monitor", "block", "investigate"]] = Field(None, description="Принятое действие")
    ioc_severity: Optional[SeverityEnum] = Field(None, description="Критичность IoC")

    # Численные и диапазоны
    priority: Optional[int] = Field(None, ge=0, description="Приоритет")
    score_min: Optional[float] = Field(None, ge=0, le=100, description="Минимальный сколл/оценка")
    score_max: Optional[float] = Field(None, ge=0, le=100, description="Максимальный сколл/оценка")

    # Сущности и флаги
    incident_id: Optional[str] = Field(None, description="ID инцидента")
    asset_id: Optional[str] = Field(None, description="ID актива")
    asset_hostname: Optional[str] = Field(None, description="Имя хоста актива")
    blacklisted: Optional[bool] = Field(None, description="Флаг нахождения в черном списке")
    text: Optional[str] = Field(None, description="Полнотекстовый поиск")

    # Пагинация (обязательные параметры с дефолтами)
    page: int = Field(default=1, ge=1, description="Номер страницы (начиная с 1)")
    size: int = Field(default=20, ge=1, le=100, description="Количество элементов на странице")


class Severity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class AssetCriticality(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class SecurityScenario(BaseModel):
    scenario_id: Optional[str] = Field(None, description="Уникальный идентификатор сценария")
    scenario_type: Optional[str] = Field(None, description="Тип сценария")
    status: Optional[str] = Field(None, description="Текущий статус сценария")
    analyst_status: Optional[AnalystStatus] = Field(None, description="Статус обработки аналитиком")
    severity: Optional[Severity] = Field(None, description="Уровень критичности")
    scenario_score: Optional[int] = Field(None, ge=0, le=100, description="Оценка риска/сценария")
    organization_id: Optional[str] = Field(None, description="Идентификатор организации")

    first_seen: Optional[datetime] = Field(None, description="Время первого обнаружения")
    last_seen: Optional[datetime] = Field(None, description="Время последнего обнаружения")

    source_ip: Optional[IPvAnyAddress] = Field(None, description="IP-адрес источника (если есть)")
    observer_host: Optional[str] = Field(None, description="Хост наблюдателя")
    destination_ip: Optional[IPvAnyAddress] = Field(None, description="IP-адрес назначения")
    destination_host: Optional[str] = Field(None, description="Хост назначения")

    asset_hostname: Optional[str] = Field(None, description="Имя хоста актива")
    asset_criticality: Optional[str] = Field(None, description="Критичность актива")

    incident_count: Optional[int] = Field(None, ge=0, description="Количество инцидентов")
    raw_event_count: Optional[int] = Field(None, ge=0, description="Количество сырых событий")
    ioc_match_count: Optional[int] = Field(None, ge=0, description="Количество совпадений по IoC")
    class Config:
        # Автоматический парсинг строк дат в формате ISO 8601
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class ScenarioApiResponse(BaseModel):
    items: list[SecurityScenario] = Field(
        default_factory=[]
    )

    total: int = Field(ge=0)
    page: int = Field(ge=1)
    size: int = Field(ge=1)


class ScenarioDetailSchema(BaseModel):
    scenario_id: str
    scenario_key: Optional[str] = None
    scenario_type: Optional[str] = None
    status: str
    engine_status: str
    analyst_status: str

    # Временные метки
    first_seen: Optional[datetime] = None
    last_seen: Optional[datetime] = None

    # Сетевые и субъектные атрибуты
    source_ip: Optional[str] = None
    source_ips: list[str] = Field(default_factory=[])
    source_user: Optional[str] = None
    source_users: list[str] = Field(default_factory=[])
    source_hosts: list[str] = Field(default_factory=[])
    observer_host: Optional[str] = None
    destination_ip: Optional[str] = None
    destination_ips: list[str] = Field(default_factory=[])
    destination_host: Optional[str] = None
    destination_hosts: list[str] = Field(default_factory=[])

    # Данные об активе (Asset)
    asset_id: Optional[str] = None
    asset_hostname: Optional[str] = None
    asset_type: Optional[str] = None
    asset_criticality: Optional[str] = None
    asset_tags: list[str] = Field(default_factory=[])

    # Запросы и полезная нагрузка
    request_uris: list[str] = Field(default_factory=[])
    payloads: list[str] = Field(default_factory=[])
    signatures: list[str] = Field(default_factory=[])

    # Хэши файлов
    file_hashes: list[str] = Field(default_factory=[])
    md5_hashes: list[str] = Field(default_factory=[])
    sha1_hashes: list[str] = Field(default_factory=[])
    sha256_hashes: list[str] = Field(default_factory=[])

    # Детекты и правила
    detection_rule_ids: list[str] = Field(default_factory=[])
    detection_categories: list[str] = Field(default_factory=[])
    detection_rule_descriptions: list[str] = Field(default_factory=[])
    recommendations: list[str] = Field(default_factory=[])

    # Индикаторы компрометации (IoC)
    ioc_matches: list[IocItemSchema] = Field(default_factory=[])
    ioc_match_count: int
    ioc_severity: Optional[str] = None
    ioc_confidence: Optional[int] = None

    # Блеклисты
    blacklisted: bool
    blacklist_sources: list[str] = Field(default_factory=[])

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True
    )


class LinksSchema(BaseModel):
    raw_events: Optional[str] = Field(default=None, description="Ссылка на сырые события")
    incidents: list[str] = Field(default_factory=[], description="Ссылки на инциденты")


class ScenarioAggregateSchema(BaseModel):
    # Поле scenario использует ранее созданную ScenarioDetailSchema
    # (или Dict[str, Any], если точно разметка не фиксирована)
    scenario: ScenarioDetailSchema = Field(description="Детальная информация о сценарии")

    incident_count: int = Field(description="Количество инцидентов")
    related_incidents: list[IncidentLiteSchema] = Field(
        default_factory=[],
        description="Связанные инциденты"
    )
    related_incident_count: int = Field(description="Количество связанных инцидентов")
    raw_event_count: int = Field(description="Количество сырых событий")

    ioc_match_count: int = Field(description="Количество совпадений IoC")
    ioc_matches: list[Any] = Field(default_factory=[], description="Совпадения IoC")

    # Пустышка для структуры MITRE (принимает любой словарь/объект)
    mitre: MitreSchema = Field(default_factory={}, description="Данные MITRE ATT&CK")

    # Вложенный объект ссылок (поддержка "links.raw_events" и "links.incidents")
    links: Optional[LinksSchema] = Field(default=None, description="Ссылки на связанную информацию")

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True
    )