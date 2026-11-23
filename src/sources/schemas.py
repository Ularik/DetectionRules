from pydantic import BaseModel, Field


class SourceCreateUpdateSchema(BaseModel):
    organization_id: str | None = Field(default=None, description="Идентификатор организации")
    name: str = Field(..., description="Наименование источника")
    source_type: str = Field(..., description="Тип источника")
    vendor_name: str | None = Field(default=None, description="Производитель")
    product_name: str | None = Field(default=None, description="Продукт")
    normalization_profile: str | None = Field(default=None, description="Профиль нормализации")
    agent_ids: list[str] = Field(default_factory=list, description="Идентификаторы агентов")
    agent_names: list[str] = Field(default_factory=list, description="Имена агентов")
    hostnames: list[str] = Field(default_factory=list, description="Имена хостов")
    locations: list[str] = Field(default_factory=list, description="Локации")
    device_ips: list[str] = Field(default_factory=list, description="IP-адреса устройств")
    health_warning_after_seconds: int = Field(default=300, ge=1, description="Порог предупреждения, сек")
    health_offline_after_seconds: int = Field(default=900, ge=1, description="Порог статуса offline, сек")
    enabled: bool = Field(default=True, description="Статус активности источника")
    description: str | None = Field(default=None, description="Описание")


class SourceSchema(SourceCreateUpdateSchema):
    source_id: str = Field(..., description="Уникальный идентификатор источника")


class SourceCreateApiResponseSchema(BaseModel):
    success: bool
    source: SourceSchema
