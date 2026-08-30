import re
from src.rules.schemas import RuleESSchema, TestRuleSchema


def match_rule(rule: RuleESSchema, test_data: TestRuleSchema) -> str | None:
    # 1. Проверка Scope
    if rule.scope and test_data.scope:
        if rule.scope != test_data.scope:
            return None

    if not rule.pattern or not rule.fields:
        return None

    # Подготовка паттерна
    target_pattern = rule.pattern if rule.case_sensitive else rule.pattern.lower()

    # Маппинг имен полей из правила (fields) на входные тестовые данные
    field_mapping = {
        "payloads": test_data.payload,
        "payload": test_data.payload,
        "request_uri": test_data.request_uri,
        "signature": test_data.signature,
    }

    # 2. Проверка совпадения по каждому полю из rule.fields
    for field_name in rule.fields:
        test_val = field_mapping.get(field_name)
        if not test_val:
            continue

        val_to_check = str(test_val) if rule.case_sensitive else str(test_val).lower()

        is_matched = False
        match_type = rule.match_type or "contains"

        # 3. Разбор match_type
        if match_type == "contains":
            is_matched = target_pattern in val_to_check
        elif match_type == "equals":
            is_matched = val_to_check == target_pattern
        elif match_type == "startswith":
            is_matched = val_to_check.startswith(target_pattern)
        elif match_type == "endswith":
            is_matched = val_to_check.endswith(target_pattern)
        elif match_type == "regex":
            flags = 0 if rule.case_sensitive else re.IGNORECASE
            is_matched = bool(re.search(rule.pattern, str(test_val), flags=flags))

        if is_matched:
            return field_name

    return None


SEVERITY_ORDER = {
    "critical": 5,
    "high": 4,
    "medium": 3,
    "low": 2,
    "info": 1
}


def sort_matches(matches: list[dict]) -> list[dict]:
    def sort_key(item: dict):
        rule: RuleESSchema = item["rule"]

        # Получаем значение enum/str для severity
        sev_value = rule.severity_hint.value if hasattr(rule.severity_hint, "value") else str(rule.severity_hint)
        sev_rank = SEVERITY_ORDER.get(sev_value.lower(), 0)

        confidence = rule.confidence or 0
        pattern_len = len(rule.pattern or "")

        return (sev_rank, confidence, pattern_len)

    return sorted(matches, key=sort_key, reverse=True)