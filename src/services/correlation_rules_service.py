import datetime

from src.correlation_rules.schemas import (CorrelationRuleCreateSchema,
        CorrelationApiResponseSchema,
        CorrelationRuleRequestCreateUpdateSchema,
        CorrelationRuleDBSchema,
        CorrelationRuleESSchema,
        CorrelationRuleUpdateESSchema,
        CorrelationRuleCreateFromOldSchema
)
from src.exceptions.exceptions import AuditNotFoundException
from src.services.base import BaseService
from src.users.schemas import UserInCookiesSchema
from src.audit.schemas import CorrelationAuditAddSchema, CorrelationAuditOutSchema


class CorrelationRuleService(BaseService):

    async def create_crule(self, user: UserInCookiesSchema,
                           data: CorrelationRuleRequestCreateUpdateSchema) -> CorrelationRuleESSchema:

        _data_in_es_schema = CorrelationRuleCreateSchema(**data.model_dump(),
                                                         created_by=user.username,
                                                         updated_by=user.username
                                                         )
        result = await self.main_backend.post("/correlation-rules", data=_data_in_es_schema)
        result = CorrelationApiResponseSchema.model_validate(result)

        data = result.rule.model_dump()
        data["created_at"] = datetime.datetime.fromisoformat(
            result.rule.created_at
        )
        data["updated_at"] = datetime.datetime.fromisoformat(
            result.rule.updated_at
        )
        _data = CorrelationRuleCreateFromOldSchema(
            **data
        )

        crule_in_db: CorrelationRuleDBSchema = await self.db.correlationModel.create_object(data=_data)

        c_audit_schema = CorrelationAuditAddSchema(author_id=user.user_id, correlation_id=result.rule.correlation_id, correlation_unique_id=crule_in_db.id)
        await self.db.correlationAuditModel.create_object(c_audit_schema)

        await self.db.save()
        return result.rule

    async def get_crules(self):
        res = await self.main_backend.get("/correlation-rules")
        return [CorrelationRuleESSchema.model_validate(r) for r in res]

    async def get_crule_detail(self, correlation_id: str):
        res = await self.main_backend.get(f"/correlation-rules/{correlation_id}")
        return CorrelationRuleESSchema.model_validate(res)

    async def put_crule(self, user: UserInCookiesSchema, correlation_id: str, data: CorrelationRuleRequestCreateUpdateSchema):

        _data_for_es = CorrelationRuleUpdateESSchema(**data.model_dump(), updated_by=user.username)
        res = await self.main_backend.put(f"/correlation-rules/{correlation_id}", _data_for_es)
        res = CorrelationApiResponseSchema.model_validate(res)

        data = res.rule.model_dump()
        data["created_at"] = datetime.datetime.fromisoformat(
            res.rule.created_at
        )
        data["updated_at"] = datetime.datetime.fromisoformat(
            res.rule.updated_at
        )

        _data = CorrelationRuleCreateFromOldSchema(
            **data
        )
        new_c_rule_version = await self.db.correlationModel.create_object(data=_data)

        old_audit: CorrelationAuditOutSchema | None = None
        try:
            old_audit: CorrelationAuditOutSchema = await self.db.correlationAuditModel.get_last_audit(correlation_id=correlation_id)
        except AuditNotFoundException:
            pass

        new_audit_schema = CorrelationAuditAddSchema(
            correlation_id=correlation_id,
            correlation_unique_id=new_c_rule_version.id,
            author_id=user.user_id,
            before_id=old_audit.id if old_audit else old_audit
        )

        new_audit = await self.db.correlationAuditModel.create_object(data=new_audit_schema)

        # обновляем старую запись для ссылки на новую
        if old_audit:
            old_audit.after_id = new_audit.id
            await self.db.correlationAuditModel.edit(id=old_audit.id, data=old_audit)

        await self.db.save()
        return res


# {
#   "enabled": true,
#   "scenario_type": "ssh_bruteforce_chain",
#   "description": "Обновленная корреляция SSH brute force и успешного входа 2",
#   "window_seconds": 1800,
#   "sequence": [
#     "ssh_bruteforce",
#     "successful_login_after_bruteforce"
#   ],
#   "group_by": [
#     "source_ip"
#   ],
#   "min_unique_categories": 2,
#   "severity_hint": "low",
#   "confidence": 90,
#   "recommendations": [
#     "Проверить успешные входы после серии неуспешных попыток"
#   ],
#   "tags": [
#     "ssh",
#     "bruteforce"
#   ],
#   "created_by": "ular",
#   "updated_by": "ular"
# }

# {
#   "enabled": true,
#   "scenario_type": "string",
#   "description": "string",
#   "window_seconds": 1,
#   "sequence": [
#     "string"
#   ],
#   "group_by": [
#     "string"
#   ],
#   "min_unique_categories": 1,
#   "severity": "critical",
#   "confidence": 100,
#   "recommendations": [
#     "string"
#   ],
#   "tags": [
#     "string"
#   ]
# }