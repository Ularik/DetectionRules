from typing import Any

from pydantic import BaseModel, ConfigDict


class ErrorResponseSchema(BaseModel):
    """Тело ответа с ошибкой (формат FastAPI HTTPException)"""
    detail: str

    model_config = ConfigDict(json_schema_extra={"examples": [{"detail": "Правило не найдено"}]})


_ERROR_DESCRIPTIONS: dict[int, tuple[str, str]] = {
    400: ("Некорректный запрос", "Такое правило уже существует"),
    401: ("Не передан или просрочен токен", "Вы не передали токен аутентификации"),
    403: ("Недостаточно прав", "Недостаточно прав для выполнения операции"),
    404: ("Объект не найден", "Правило не найдено"),
    409: ("Конфликт с существующим объектом", "Значение с таким value уже есть в справочнике"),
    502: ("Ошибка или недоступность внешнего API", "Ошибка внешнего API"),
    503: ("Elasticsearch недоступен", "Хранилище правил (Elasticsearch) недоступно, попробуйте позже"),
    504: ("Внешний сервис не ответил вовремя", "Внешний сервис не ответил вовремя"),
}


def error_responses(*codes: int) -> dict[int | str, dict[str, Any]]:
    """Описания ошибок для параметра `responses` у роутов (для OpenAPI)"""
    return {
        code: {
            "model": ErrorResponseSchema,
            "description": _ERROR_DESCRIPTIONS[code][0],
            "content": {"application/json": {"example": {"detail": _ERROR_DESCRIPTIONS[code][1]}}},
        }
        for code in codes
    }
