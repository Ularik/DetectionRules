from typing import List
from pydantic import BaseModel, Field, ConfigDict


class OrganizationCreateUpdateSchema(BaseModel):
    name: str
    aliases: list[str] = Field(default=list)
    agent_ids: list[str] = Field(default=list)
    hostnames: list[str] = Field(default=list)
    enabled: bool = Field(default=False)


class Organization(BaseModel):
    organization_id: str = Field(..., description="Уникальный идентификатор организации")
    name: str = Field(..., description="Наименование организации")
    aliases: List[str] = Field(default_factory=[], description="Альтернативные названия/псевдонимы")
    agent_names: List[str] = Field(default_factory=[], description="Имена агентов")
    agent_ids: List[str] = Field(default_factory=[], description="Идентификаторы агентов")
    hostnames: List[str] = Field(default_factory=[], description="Имена хостов")
    enabled: bool = Field(default=True, description="Статус активности организации")


class OrganizationCreateApiResponseSchema(BaseModel):
    success: bool
    organization: Organization


class OrganizationListApiResponse(BaseModel):
    items: List[Organization] = Field(default_factory=[], description="Список организаций")


class AgentsSchema(BaseModel):
    agent_id: str
    agent_name: str
    status: str

    model_config = ConfigDict(extra="ignore")


class AgentsApiResponseSchema(BaseModel):
    items: list[AgentsSchema]
    total: int
