from typing import List
from pydantic import BaseModel, Field


class Organization(BaseModel):
    organization_id: str = Field(..., description="Уникальный идентификатор организации")
    name: str = Field(..., description="Наименование организации")
    aliases: List[str] = Field(default_factory=[], description="Альтернативные названия/псевдонимы")
    agent_names: List[str] = Field(default_factory=[], description="Имена агентов")
    agent_ids: List[str] = Field(default_factory=[], description="Идентификаторы агентов")
    hostnames: List[str] = Field(default_factory=[], description="Имена хостов")
    enabled: bool = Field(default=True, description="Статус активности организации")


class OrganizationListApiResponse(BaseModel):
    items: List[Organization] = Field(default_factory=[], description="Список организаций")