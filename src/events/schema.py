from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class RawEventsQueryParamsSchema(BaseModel):
    from_time: Optional[datetime] = Field(default=None, description="Начало временного интервала")
    to_time: Optional[datetime] = Field(default=None, description="Конец временного интервала")

    source_ip: Optional[str] = Field(default=None, description="IP-адрес источника")
    destination_ip: Optional[str] = Field(default=None, description="IP-адрес назначения")
    host: Optional[str] = Field(default=None, description="Имя хоста")
    user: Optional[str] = Field(default=None, description="Имя пользователя")

    agent_name: Optional[str] = Field(default=None, description="Имя агента Wazuh")
    agent_ip: Optional[str] = Field(default=None, description="IP-адрес агента")
    location: Optional[str] = Field(default=None, description="Локация/лог-файл источника")
    decoder: Optional[str] = Field(default=None, description="Имя декодера")
    program_name: Optional[str] = Field(default=None, description="Имя программы/системного процесса")
    rule_id: Optional[str] = Field(default=None, description="ID правила корреляции/детекта")
    text: Optional[str] = Field(default=None, description="Полнотекстовый поиск по логу")

    page: int = Field(default=1, ge=1, description="Номер страницы (начиная с 1)")
    size: int = Field(default=50, ge=1, le=1000, description="Количество записей на страницу")

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True
    )


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


class WazuhEventApiResponseSchema(BaseModel):
    items: list[WazuhEventSchema]
    total: int
    page: int
    size: int
