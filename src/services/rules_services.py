from src.exceptions.exceptions import ObjectNotFoundException, RuleNotFoundException
from src.services.base import BaseService
from src.rules.schemas import RuleRequestCreateSchema, RuleInDbSchema, \
    RuleESSchema, RuleUpdateSchema, RuleUpdateElasticSchema
from src.audit.schemas import AuditAddSchema, AuditOutSchema

from src.users.schemas import UserInCookiesSchema


class RuleService(BaseService):

    async def find_rules(self,
                         pattern: str = None,
                         description: str = None,
                         rule_id: str = None,
                         limit: int = 10,
                         offset: int = 0) -> dict | None:
        text = pattern or description

        if rule_id:
            return await self.es.rulesRepository.get_by_id(doc_id=rule_id)
        return await self.es.rulesRepository.search_rules(text=text, limit=limit, offset=offset)


    async def find_one(self, rule_id: str) -> dict:
        try:
            return await self.es.rulesRepository.get_by_id(doc_id=rule_id)
        except ObjectNotFoundException as err:
            raise RuleNotFoundException from err


    async def create_rule(self, user: UserInCookiesSchema, data: RuleRequestCreateSchema) -> dict:
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

    async def update_rule(self, user: UserInCookiesSchema, rule_id: str, data: RuleUpdateSchema):

        # создаем новый объект в БД с новым unique_id
        data = RuleRequestCreateSchema(rule_id=rule_id, **data.model_dump())
        new_rule_version: RuleInDbSchema = await self.db.ruleModel.create_object(data)

        # вытаскиваем последнюю запись в истории для обновления after_id
        old_audit: AuditOutSchema = await self.db.auditModel.get_last_audit(rule_general_id=rule_id)

        # создаем новую запись в истории с before_id = old_audit.id
        new_audit_data = AuditAddSchema(
            rule_unique_id=new_rule_version.unique_id,
            author_id=user.user_id,
            rule_general_id=rule_id,
            before_id=old_audit.id
        )
        new_audit: AuditOutSchema = await self.db.auditModel.create_object(new_audit_data)

        # обновляем старую запись для ссылки на новую
        old_audit.after_id = new_audit.id
        await self.db.auditModel.edit(id=old_audit.id, data=old_audit)

        await self.db.save()

        _rule_elastic_data = RuleUpdateElasticSchema.model_validate(
            {**new_rule_version.model_dump(),  # меняем id авторов на имена
             "updated_by": user.username
             }
        )

        res: RuleESSchema = await self.es.rulesRepository.update_rule(rule_id=rule_id, data=_rule_elastic_data)

        return res


    async def delete(self, rule_id: str):
        await self.db.ruleModel.delete_bulk(rule_id=rule_id)
        await self.db.save()
        return await self.es.rulesRepository.delete(doc_id=rule_id)
