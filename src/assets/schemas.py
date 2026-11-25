from enum import Enum
from pydantic import BaseModel, Field


class AssetType(str, Enum):
    server = "server"
    web_server = "web_server"
    database = "database"
    workstation = "workstation"
    firewall = "firewall"
    waf = "waf"
    ips = "ips"
    router = "router"
    switch = "switch"
    domain_controller = "domain_controller"
    wazuh_manager = "wazuh_manager"
    elasticsearch = "elasticsearch"
    application = "application"
    other = "other"


class AssetCriticality(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"
    critical = "critical"


class AssetEnvironment(str, Enum):
    prod = "prod"
    test = "test"
    dev = "dev"
    stage = "stage"
    lab = "lab"


class AssetCreateUpdateSchema(BaseModel):
    """Тело POST /assets и PUT /assets/{asset_id} (AssetCreate / AssetUpdate движка)."""
    organization_id: str = Field(..., description="Идентификатор организации")
    name: str = Field(..., description="Наименование актива")
    ip: str = Field(..., description="IP-адрес")
    hostnames: list[str] = Field(default_factory=list, description="Имена хостов")
    asset_type: AssetType | None = Field(default=None, description="Тип актива")
    criticality: AssetCriticality = Field(default=AssetCriticality.medium, description="Критичность")
    environment: AssetEnvironment | None = Field(default=None, description="Окружение")
    tags: list[str] = Field(default_factory=list, description="Теги")
    enabled: bool = Field(default=True, description="Статус активности актива")
    description: str | None = Field(default=None, description="Описание")
