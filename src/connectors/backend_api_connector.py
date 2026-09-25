import logging
from typing import Any
import aiohttp
from pydantic import BaseModel

from src.config import settings

logger = logging.getLogger(__name__)


class BackendApi:

    def __init__(self, url: str, timeout: int = 10):
        self.url = url
        self.timeout = aiohttp.ClientTimeout(total=timeout)
        self.client: aiohttp.ClientSession | None = None

    async def connect(self):
        if self.client is None or self.client.closed:
            self.client = aiohttp.ClientSession(
                base_url=self.url,
                timeout=self.timeout
            )

    async def close(self):
        if self.client and not self.client.closed:
            await self.client.close()

    async def health(self) -> bool:
        try:
            await self.request('GET', '/health')
            logger.info("Связь с Backend API установлена")
            return True
        except Exception as err:
            logger.error("Ошибка при проверке health Backend API: %s", err)
            return False

    async def _prepare_json_data(self, data: Any) -> Any:
        """Приводит Pydantic-модели к JSON-совместимому виду."""
        if isinstance(data, BaseModel):
            return data.model_dump(mode='json', by_alias=True)
        return data

    async def request(
        self,
        method: str,
        endpoint: str,
        *,
        data: Any = None,
        params: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
    ) -> Any:
        """Централизованный метод отправки HTTP-запросов."""
        if self.client is None or self.client.closed:
            raise RuntimeError("BackendApi client is not connected. Call connect() first.")

        json_payload = await self._prepare_json_data(data)

        try:
            async with self.client.request(
                method=method,
                url=endpoint,
                json=json_payload,
                params=params,
                headers=headers,
            ) as response:
                # Поднимает aiohttp.ClientResponseError при статусах 4xx/5xx
                response.raise_for_status()

                # Если ответ пустой (например, 204 No Content)
                if response.status == 204:
                    return None

                return await response.json()

        except aiohttp.ClientResponseError as err:
            logger.error(
                "Backend API вернул ошибку %s при %s %s: %s",
                err.status, method, endpoint, err.message
            )
            raise
        except aiohttp.ClientError as err:
            logger.error("Сетевая ошибка при запросе %s %s: %s", method, endpoint, err)
            raise

    async def get(self, endpoint: str, params: dict[str, Any] | None = None, **kwargs) -> Any:
        return await self.request('GET', endpoint, params=params, **kwargs)

    async def post(self, endpoint: str, data: Any = None, **kwargs) -> Any:
        return await self.request('POST', endpoint, data=data, **kwargs)

    async def put(self, endpoint: str, data: Any = None, **kwargs) -> Any:
        return await self.request('PUT', endpoint, data=data, **kwargs)

    async def patch(self, endpoint: str, data: Any = None, **kwargs) -> Any:
        return await self.request('PATCH', endpoint, data=data, **kwargs)

    async def delete(self, endpoint: str, **kwargs) -> Any:
        return await self.request('DELETE', endpoint, **kwargs)


backend_api = BackendApi(settings.BACKEND_API_URL)