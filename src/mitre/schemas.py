from datetime import datetime
from typing import List
from pydantic import BaseModel, Field


class MitreTechniqueResponseSchema(BaseModel):
    """Схема одной техники MITRE ATT&CK, возвращаемая клиенту."""

    mitre_id: str = Field(..., description="ID техники MITRE, например T1001", example="T1001")
    stix_id: str = Field(..., description="Внутренний STIX-идентификатор объекта")
    name: str = Field(..., description="Название техники")
    description: str = Field(..., description="Подробное описание техники")
    tactics: List[str] = Field(default_factory=list, description="Список тактик MITRE")
    platforms: List[str] = Field(default_factory=list, description="Применимые платформы (например, Linux, Windows)")
    is_subtechnique: bool = Field(False, description="Является ли техника подтехникой")
    revoked: bool = Field(False, description="Отозвана ли техника MITRE")
    deprecated: bool = Field(False, description="Устарела ли техника")
    modified: datetime = Field(..., description="Дата последнего изменения в MITRE")
    version: str = Field(..., description="Версия техники")
    source_url: str = Field(..., description="Ссылка на официальную страницу MITRE")
    domain: str = Field("enterprise-attack", description="Домен ATT&CK")
    source: str = Field("MITRE ATT&CK", description="Источник данных")
    synced_at: datetime = Field(..., description="Дата и время синхронизации в системе")

    class Config:
        from_attributes = True  # Позволяет мапить данные из ORM-моделей (SQLAlchemy) напрямую


class MitreSyncResponseSchema(BaseModel):
    """Схема ответа после запуска ручной/административной синхронизации с TAXII."""

    success: bool = Field(..., description="Статус выполнения синхронизации")
    source: str = Field(..., description="Источник получения данных")
    received: int = Field(..., description="Получено объектов от источника")
    indexed: int = Field(..., description="Записано/обновлено в локальном индексе")
    active: int = Field(..., description="Количество активных техник")
    revoked: int = Field(..., description="Количество отозванных объектов")
    deprecated: int = Field(..., description="Количество устаревших объектов")
    skipped: int = Field(..., description="Пропущено объектов")
    synced_at: datetime = Field(..., description="Точное время завершения синхронизации в UTC")

class MitreSchema(BaseModel):
    ids: list[str]
    tactics: list[str]
    techniques: list[str]