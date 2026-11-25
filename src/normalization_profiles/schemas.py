from typing import Any, Literal

from pydantic import BaseModel, Field


class NormalizationProfileSchema(BaseModel):
    """Профиль нормализации: соответствие полей СЗИ внутренним полям SIEM"""
    source_name: str
    source_type: str
    format: Literal["json", "syslog", "cef", "leef", "kv", "text"] = "json"
    enabled: bool = True
    description: str = ""
    field_mapping: dict[str, list[str]] = Field(default_factory=dict)


class NormalizationProfileTestSchema(BaseModel):
    """Проверка mapping на raw-событии без сохранения профиля"""
    profile: NormalizationProfileSchema
    raw_event: dict[str, Any]
