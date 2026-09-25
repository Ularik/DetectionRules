from datetime import datetime
from typing import Literal, TypeVar, Generic

from pydantic import BaseModel, Field


class IocCreateSchema(BaseModel):
    ioc_type: str
    value: str


class IocItemSchema(BaseModel):
    ioc_id: str
    ioc_type: str
    value: str
    threat_type: str
    severity: str
    confidence: int = Field(ge=0, le=100)
    source: str
    source_org: str | None = None
    description: str | None = None
    tags: list[str] = Field(default_factory=[])

    # MISP метаданные (могут быть None, если источник не MISP)
    misp_event_id: str | None = None
    misp_event_uuid: str | None = None
    misp_attribute_id: str | None = None
    misp_attribute_uuid: str | None = None
    to_ids: bool = False

    # Временные метки и статус просмотра
    last_seen_at: datetime
    received_at: datetime
    viewed: bool = False
    viewed_at: datetime | None = None
    viewed_by: str | None = None


class IocItemPatchcSchema(BaseModel):
    success: bool
    ioc: IocItemSchema


T = TypeVar('T')


class PaginatedResponse(BaseModel, Generic[T]):
    items: list[T]
    total: int = Field(ge=0)
    page: int = Field(ge=1)
    size: int = Field(ge=1)
    pages: int = Field(ge=0)
    has_next: bool
    has_previous: bool