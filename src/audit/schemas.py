from typing import Any

from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from src.rules.schemas import RuleDBSchema
from src.correlation_rules.schemas import CorrelationRuleDBSchema
from src.users.schemas import UserOutSchema


class AuditAddSchema(BaseModel):
    author_id: int
    rule_unique_id: int
    rule_general_id: str
    action: str | None = Field(default='created')
    resource_type: str | None = None
    before_id: int | None = None
    after_id: int | None = None


class AuditOutSchema(AuditAddSchema):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True, extra="ignore")


class AuditOutWithAuthorSchema(AuditOutSchema):
    author: UserOutSchema


class ApiAuditWithAuthorSchema(BaseModel):
    total: int
    items: list[AuditOutWithAuthorSchema]


class AuditOutFullSchema(AuditOutWithAuthorSchema):
    rule: RuleDBSchema


## Correlation audit
class CorrelationAuditAddSchema(BaseModel):
    author_id: int
    correlation_unique_id: int
    correlation_id: str
    action: str | None = Field(default='created')
    resource_type: str | None = None
    before_id: int | None = None
    after_id: int | None = None


class CorrelationAuditOutSchema(CorrelationAuditAddSchema):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True, extra="ignore")


_CORRELATION_AUDIT_EXAMPLE = {
    "id": 3,
    "author_id": 1,
    "correlation_unique_id": 6,
    "correlation_id": "CORR-0031399A",
    "action": "updated",
    "resource_type": None,
    "before_id": 2,
    "after_id": None,
    "created_at": "2026-09-25T10:51:45.405097+00:00",
    "updated_at": "2026-09-25T10:51:45.405097+00:00",
    "author": {"id": 1, "username": "ular", "role": "ADMIN"},
}


class CorrelationAuditOutWithAuthorSchema(CorrelationAuditOutSchema):
    author: UserOutSchema

    model_config = ConfigDict(from_attributes=True, extra="ignore",
                              json_schema_extra={"examples": [_CORRELATION_AUDIT_EXAMPLE]})


class ApiCorrelationAuditWithAuthorSchema(BaseModel):
    """Страница истории изменений правил корреляции (новые записи первыми)"""
    total: int
    has_next: bool
    items: list[CorrelationAuditOutWithAuthorSchema]

    model_config = ConfigDict(json_schema_extra={
        "examples": [{"total": 1, "has_next": False, "items": [_CORRELATION_AUDIT_EXAMPLE]}]
    })


class AuditFieldChangeSchema(BaseModel):
    """Изменение одного поля правила относительно предыдущей версии"""
    field: str
    old: Any = None
    new: Any = None


# служебные поля версии, которые не показываем как изменения
_NOT_DIFFED_FIELDS = {"id", "created_at", "updated_at", "created_by", "updated_by", "correlation_id"}


def diff_versions(before: BaseModel | None, after: BaseModel) -> list[AuditFieldChangeSchema]:
    """Список полей, отличающихся между двумя версиями правила"""
    if before is None:
        return []
    old, new = before.model_dump(mode="json"), after.model_dump(mode="json")
    return [
        AuditFieldChangeSchema(field=key, old=old.get(key), new=new.get(key))
        for key in new
        if key not in _NOT_DIFFED_FIELDS and old.get(key) != new.get(key)
    ]


class CorrelationAuditOutFullSchema(CorrelationAuditOutWithAuthorSchema):
    """Запись истории с версией правила на этот момент и списком изменений относительно предыдущей версии"""
    rule: CorrelationRuleDBSchema
    changes: list[AuditFieldChangeSchema] = Field(
        default_factory=list,
        description="Что изменилось относительно предыдущей записи (before_id); пусто для первой версии",
    )

    model_config = ConfigDict(from_attributes=True, extra="ignore", json_schema_extra={"examples": [{
        **_CORRELATION_AUDIT_EXAMPLE,
        "rule": {
            "id": 6,
            "correlation_id": "CORR-0031399A",
            "enabled": True,
            "scenario_type": "linux_privilege_escalation_chain",
            "description": "Вход или выполнение команд с последующим повышением привилегий",
            "window_seconds": 1800,
            "sequence": ["network_scan"],
            "group_by": ["path_traversal", "source_ip"],
            "min_unique_categories": 30,
            "severity": "critical",
            "confidence": 85,
            "recommendations": ["Проверить sudo/root активность пользователя."],
            "tags": ["linux", "privilege_escalation"],
            "mitre_ids": ["T1068"],
            "created_by": "dev",
            "updated_by": "dev",
            "created_at": "2026-09-25T08:41:04.283735+00:00",
            "updated_at": "2026-09-25T09:51:46.650107+00:00",
        },
        "changes": [
            {"field": "min_unique_categories", "old": 2, "new": 30},
            {"field": "group_by", "old": ["source_ip"], "new": ["path_traversal", "source_ip"]},
            {"field": "mitre_ids", "old": [], "new": ["T1068"]},
        ],
    }]})

# ---------- журнал аудита внешнего API (GET /audit) ----------

class EngineAuditQuerySchema(BaseModel):
    size: int = Field(default=100, ge=1, description="Количество записей")
    resource_type: str | None = Field(
        default=None,
        description="Тип ресурса: detection_rule, correlation_rule, suppression_rule, threat_intel_ioc, "
                    "organization, source, asset, mitre_mapping, engine_settings и др.",
    )
    action: str | None = Field(
        default=None,
        description="Действие: create, update, delete, enable, disable, publish, mark_viewed, sync и др.",
    )
    resource_id: str | None = Field(default=None, description="Идентификатор ресурса (rule_id, correlation_id и т.д.)")
    organization_id: str | None = Field(default=None, description="Идентификатор организации")


class EngineAuditSchema(BaseModel):
    """Запись журнала аудита внешнего API: снимки ресурса до и после действия."""
    audit_id: str = Field(..., description="Идентификатор записи аудита")
    timestamp: datetime = Field(..., description="Время действия")
    actor: str | None = Field(None, description="Пользователь, выполнивший действие")
    role: str | None = Field(None, description="Роль пользователя")
    action: str = Field(..., description="Действие")
    resource_type: str = Field(..., description="Тип ресурса")
    resource_id: str | None = Field(None, description="Идентификатор ресурса")
    organization_id: str | None = Field(None, description="Идентификатор организации")
    before: dict[str, Any] | None = Field(None, description="Состояние ресурса до действия")
    after: dict[str, Any] | None = Field(None, description="Состояние ресурса после действия")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Дополнительные данные")
