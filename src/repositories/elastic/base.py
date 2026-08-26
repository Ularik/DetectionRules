from elastic_transport import ObjectApiResponse
from elasticsearch import AsyncElasticsearch, ConflictError, NotFoundError

from src.exceptions.exceptions import ObjectNotFoundException, NoResultException, RuleAlreadyExistException


class ElasticRepository:
    INDEX = ''

    def __init__(self, client: AsyncElasticsearch):
        self.client = client

    async def get_by_id(self, doc_id: str) -> dict:
        result = await self.client.get(index=self.INDEX, id=doc_id, ignore=[404])
        if not result.get("found"):
            raise ObjectNotFoundException
        return result["_source"]

    async def search(self, query: dict) -> (list[dict], int):
        query["sort"] = [{"created_at": {"order": "desc"}}]
        result = await self.client.search(index=self.INDEX, body=query)
        total = result["hits"]["total"]["value"]  # общее кол-во записей
        items = [hit["_source"] for hit in result["hits"]["hits"]]
        return items, total

    async def create(self, doc_id: str, body: dict) -> dict | ObjectApiResponse:
        try:
            await self.client.create(index=self.INDEX, id=doc_id, document=body)
            return await self.get_by_id(doc_id=doc_id)
        except ConflictError:
            raise RuleAlreadyExistException

    async def update(self, doc_id: str, body: dict) -> dict:
        try:
            await self.client.update(index=self.INDEX, id=doc_id, body={"doc": body})
            return await self.get_by_id(doc_id)
        except NotFoundError:
            raise ObjectNotFoundException

    async def delete(self, doc_id: str) -> dict | ObjectApiResponse:
        try:
            return await self.client.delete(index=self.INDEX, id=doc_id, refresh="wait_for")
        except NotFoundError:
            raise ObjectNotFoundException