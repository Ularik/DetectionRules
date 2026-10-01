from datetime import datetime
from src.incidents.schemas import AnalystStatus
from enum import Enum
from typing import Optional, Literal
from pydantic import BaseModel, Field, IPvAnyAddress


class SeverityEnum(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


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