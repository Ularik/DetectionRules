import logging
from contextlib import contextmanager

from elastic_transport import ObjectApiResponse, TransportError
from elasticsearch import AsyncElasticsearch, ConflictError, NotFoundError, BadRequestError, ApiError

from src.exceptions.exceptions import (
    ObjectNotFoundException,
    RuleAlreadyExistException,
    InvalidSearchParamsException,
    StorageUnavailableException,
)

logger = logging.getLogger(__name__)


@contextmanager
def _handle_es_errors():
    """Переводит низкоуровневые ошибки ES в исключения приложения.
    ConflictError/NotFoundError не трогаем — их обрабатывают конкретные методы."""
    try:
        yield
    except (ConflictError, NotFoundError):
        raise
    except BadRequestError as err:
        logger.warning("ES отклонил запрос: %s", err)
        raise InvalidSearchParamsException from err
    except TransportError as err:  # нет соединения, таймаут, TLS
        logger.error("Elasticsearch недоступен: %s", err)
        raise StorageUnavailableException from err
    except ApiError as err:  # прочие ответы ES с ошибкой (5xx, 401/403 по кредам и т.д.)
        logger.error("Ошибка Elasticsearch: %s", err)
        raise StorageUnavailableException from err


class ElasticRepository:
    INDEX = ''

    def __init__(self, client: AsyncElasticsearch):
        self.client = client

    async def get_by_id(self, doc_id: str) -> dict:
        with _handle_es_errors():
            result = await self.client.get(index=self.INDEX, id=doc_id, ignore=[404])
        if not result.get("found"):
            raise ObjectNotFoundException
        return result["_source"]

    async def search(self, query: dict) -> tuple[list[dict], int]:
        query["sort"] = [{"created_at": {"order": "desc", "unmapped_type": "date"}}]
        query["track_total_hits"] = True  # иначе total ограничен 10000
        try:
            with _handle_es_errors():
                result = await self.client.search(index=self.INDEX, body=query)
        except NotFoundError:  # индекса ещё нет — значит, и документов нет
            return [], 0
        total = result["hits"]["total"]["value"]  # общее кол-во записей
        items = [hit["_source"] for hit in result["hits"]["hits"]]
        return items, total

    async def create(self, doc_id: str, body: dict) -> dict:
        try:
            with _handle_es_errors():
                await self.client.create(index=self.INDEX, id=doc_id, document=body, refresh="wait_for")
            return await self.get_by_id(doc_id=doc_id)
        except ConflictError:
            raise RuleAlreadyExistException

    async def update(self, doc_id: str, body: dict) -> dict:
        try:
            with _handle_es_errors():
                await self.client.update(index=self.INDEX, id=doc_id, body={"doc": body}, refresh="wait_for")
            return await self.get_by_id(doc_id)
        except NotFoundError:
            raise ObjectNotFoundException

    async def delete(self, doc_id: str) -> ObjectApiResponse:
        try:
            with _handle_es_errors():
                return await self.client.delete(index=self.INDEX, id=doc_id, refresh="wait_for")
        except NotFoundError:
            raise ObjectNotFoundException
