import logging

import aiohttp
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from src.exceptions import exceptions

logger = logging.getLogger(__name__)

# статусы внешнего API, которые имеет смысл отдать фронту как есть (ошибка в данных запроса)
_PASS_THROUGH_STATUSES = {400, 404, 409, 422}


def _error(status_code: int, detail: str) -> JSONResponse:
    return JSONResponse(status_code=status_code, content={"detail": detail})


def setup_exceptions(app: FastAPI):

    @app.exception_handler(exceptions.RuleNotFoundException)
    async def rule_not_found_exception_handler(request: Request, exc: exceptions.RuleNotFoundException):
        return _error(404, exc.detail)

    @app.exception_handler(exceptions.AuditNotFoundException)
    async def audit_not_found_exception_handler(request: Request, exc: exceptions.AuditNotFoundException):
        return _error(404, exc.detail)

    @app.exception_handler(exceptions.RuleAlreadyExistException)
    async def rule_already_exist_exception_handler(request: Request, exc: exceptions.RuleAlreadyExistException):
        return _error(400, exc.detail)

    @app.exception_handler(exceptions.InvalidSearchParamsException)
    async def invalid_search_params_handler(request: Request, exc: exceptions.InvalidSearchParamsException):
        return _error(400, exc.detail)

    @app.exception_handler(exceptions.StorageUnavailableException)
    async def storage_unavailable_handler(request: Request, exc: exceptions.StorageUnavailableException):
        return _error(503, exc.detail)

    @app.exception_handler(aiohttp.ClientResponseError)
    async def backend_api_response_error_handler(request: Request, exc: aiohttp.ClientResponseError):
        logger.error("Внешний API вернул %s на %s: %s", exc.status, exc.request_info.real_url, exc.message)
        if exc.status == 404:
            return _error(404, "Объект не найден во внешнем API")
        if exc.status in _PASS_THROUGH_STATUSES:
            return _error(exc.status, f"Внешний API отклонил запрос: {exc.message}")
        # 401/403/5xx внешнего API — проблема на нашей стороне или у движка, а не у пользователя
        return _error(502, "Ошибка внешнего API")

    @app.exception_handler(aiohttp.ClientConnectionError)
    async def backend_api_connection_error_handler(request: Request, exc: aiohttp.ClientConnectionError):
        logger.error("Внешний API недоступен: %s", exc)
        return _error(502, "Внешний API недоступен")

    @app.exception_handler(TimeoutError)
    async def backend_api_timeout_handler(request: Request, exc: TimeoutError):
        logger.error("Таймаут запроса: %s", request.url.path)
        return _error(504, "Внешний сервис не ответил вовремя")
