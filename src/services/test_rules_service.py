from src.rules.schemas import TestRuleSchema, RuleApiResponseSchema
from src.services.base import BaseService
from src.utils.mutch_rule import match_rule, sort_matches


class TestRuleService(BaseService):

    async def test_rules(self, test_data: TestRuleSchema):
        rules_response: RuleApiResponseSchema = await self.es.rulesRepository.search_rules(
            text=None,
            enabled_only=True,
            limit=1000
        )

        matched_results = []

        # 2. Проверяем каждое правило из items (список RuleESSchema)
        for rule in rules_response.items:
            matched_field = match_rule(rule, test_data)
            if matched_field:
                # Формируем структуру ответа согласно ТЗ (раздел 5.8)
                rule_dict = rule.model_dump()
                rule_dict["matched_field"] = matched_field
                rule_dict["rule"] = rule  # Сохраняем объект схемы для удобства сортировки
                matched_results.append(rule_dict)

        # Если совпадений нет — возвращаем стандартный ответ (раздел 5.9)
        if not matched_results:
            return {
                "matched": False,
                "matches": [],
                "message": "No detection rule matched the provided test payload"
            }

        # 3. Сортируем сработавшие правила по приоритету
        sorted_matches = sort_matches(matched_results)

        # Удаляем временное вспомогательное поле 'rule' перед отдачей в API
        for item in sorted_matches:
            item.pop("rule", None)

        return {
            "matched": True,
            "matches": sorted_matches
        }