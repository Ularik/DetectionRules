from src.exceptions.exceptions import ObjectNotFoundException, RuleNotFoundException, AuditNotFoundException, \
    InvalidSearchParamsException
from src.services.base import BaseService
from src.rules.schemas import RuleRequestCreateUpdateSchema, RuleInDbSchema, RuleApiResponseSchema, \
    RuleESSchema, RuleSetStatusSchema, RuleSetStatusApiResponseSchema, TestRuleSchema, TestRuleResponseSchema, \
    RuleDeleteResponseSchema
from src.audit.schemas import AuditAddSchema, AuditOutSchema, AuditOutWithAuthorSchema

from src.users.schemas import UserInCookiesSchema

# index.max_result_window в ES по умолчанию: дальше from + size поиск не листает
ES_MAX_RESULT_WINDOW = 10_000


def _clean(value: str | None) -> str | None:
    """Пустые строки и строки из пробелов считаем отсутствующим фильтром"""
    if value is None:
        return None
    value = value.strip()
    return value or None


class RuleService(BaseService):

    async def find_rules(self,
                         pattern: str | None = None,
                         description: str | None = None,
                         rule_id: str | None = None,
                         limit: int = 10,
                         offset: int = 0) -> RuleApiResponseSchema:
        """Поиск правил в ES. Всегда возвращает страницу {total, has_next, items}:
        с rule_id — страницу из 0 или 1 правила, иначе — полнотекстовый поиск по pattern и description."""
        if offset + limit > ES_MAX_RESULT_WINDOW:
            raise InvalidSearchParamsException(
                f"Нельзя пролистать дальше {ES_MAX_RESULT_WINDOW} записей: уточните условия поиска"
            )

        pattern, description, rule_id = _clean(pattern), _clean(description), _clean(rule_id)

        if rule_id:
            try:
                rule = await self.es.rulesRepository.get_one_rule(doc_id=rule_id)
            except ObjectNotFoundException:
                return RuleApiResponseSchema(total=0, has_next=False, items=[])
            return RuleApiResponseSchema(total=1, has_next=False, items=[rule] if offset == 0 else [])

        return await self.es.rulesRepository.search_rules(
            pattern=pattern, description=description, limit=limit, offset=offset
        )


    async def find_one(self, rule_id: str) -> RuleESSchema:
        try:
            return await self.es.rulesRepository.get_one_rule(doc_id=rule_id)
        except ObjectNotFoundException as err:
            raise RuleNotFoundException from err


    async def create_rule(self, user: UserInCookiesSchema, data: RuleRequestCreateUpdateSchema) -> dict:
        rule_data_with_unique_id: RuleInDbSchema = await self.db.ruleModel.create_object(data)

        _audit_data = AuditAddSchema(author_id=user.user_id, rule_unique_id=rule_data_with_unique_id.unique_id, rule_general_id=data.rule_id)
        await self.db.auditModel.create_object(_audit_data)

        _rule_elastic_data = RuleESSchema.model_validate(
            {**rule_data_with_unique_id.model_dump(),   # меняем id авторов на имена
             "created_by": user.username,
             "updated_by": user.username
             }
        )
        res = await self.es.rulesRepository.create_rule(_rule_elastic_data)
        await self.db.save()
        return res


    async def set_status(self, rule_id: str, data: RuleSetStatusSchema) -> RuleESSchema:
        response = await self.main_backend.patch(f"/detection-rules/{rule_id}/status", data=data)
        return RuleSetStatusApiResponseSchema.model_validate(response).rule


    async def update_rule(self, user: UserInCookiesSchema, rule_id: str, data: RuleRequestCreateUpdateSchema):

        # текущая версия из ES: нужна для created_by/created_at, заодно 404 если правила нет
        current_rule: RuleESSchema = await self.find_one(rule_id)

        # rule_id неизменяемый — берем из пути, а не из тела
        data = data.model_copy(update={"rule_id": rule_id})

        # создаем новый объект в БД с новым unique_id
        new_rule_version: RuleInDbSchema = await self.db.ruleModel.create_object(data)

        # вытаскиваем последнюю запись в истории для обновления after_id
        old_audit: AuditOutSchema | None = None
        try:
            old_audit: AuditOutSchema = await self.db.auditModel.get_last_audit(rule_id=rule_id)
        except AuditNotFoundException:
            pass

        # создаем новую запись в истории с before_id = old_audit.id
        new_audit_data = AuditAddSchema(
            rule_unique_id=new_rule_version.unique_id,
            author_id=user.user_id,
            action="updated",
            resource_type=rule_id,
            rule_general_id=data.rule_id,
            before_id=old_audit.id if old_audit else old_audit
        )
        new_audit: AuditOutSchema = await self.db.auditModel.create_object(new_audit_data)

        # обновляем старую запись для ссылки на новую
        if old_audit:
            old_audit.after_id = new_audit.id
            await self.db.auditModel.edit(id=old_audit.id, data=old_audit)

        _rule_elastic_data = RuleESSchema.model_validate(
            {**new_rule_version.model_dump(),  # меняем id авторов на имена
             "created_by": current_rule.created_by,
             "created_at": current_rule.created_at,
             "updated_by": user.username
             }
        )
        # сначала ES, потом commit: если ES упадет, версия в PG откатится
        res: RuleESSchema = await self.es.rulesRepository.update_rule(doc_id=rule_id, data=_rule_elastic_data)
        await self.db.save()

        return res


    async def test_rule(self, data: TestRuleSchema) -> TestRuleResponseSchema:
        result = await self.main_backend.post("/detection-rules/test", data=data)
        return TestRuleResponseSchema.model_validate(result)


    async def delete(self, rule_id: str) -> RuleDeleteResponseSchema:
        # 404 до любых изменений; commit в PG только после успешного удаления из ES
        await self.find_one(rule_id)
        await self.db.ruleModel.delete_bulk(rule_id=rule_id)
        try:
            res = await self.es.rulesRepository.delete(doc_id=rule_id)
        except ObjectNotFoundException as err:
            raise RuleNotFoundException from err
        await self.db.save()
        return RuleDeleteResponseSchema.model_validate(res.body)

    async def get_detection_categories(self):
        return await self.main_backend.get("/detection-categories")

    async def get_detection_scopes(self):
        return await self.main_backend.get("/detection-scopes")
