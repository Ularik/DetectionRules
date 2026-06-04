from elasticsearch import AsyncElasticsearch
from elasticsearch import NotFoundError

from src.exceptions import ObjectNotFoundException


class ElasticRepository:
    INDEX = ''

    def __init__(self, client: AsyncElasticsearch):
        self.client = client

    async def get_by_id(self, doc_id: str) -> dict | None:
        result = await self.client.get(index=self.INDEX, id=doc_id, ignore=[404])
        return result["_source"] if result.get("found") else None

    async def search(self, query: dict) -> (list[dict], int):
        result = await self.client.search(index=self.INDEX, body=query)
        total = result["hits"]["total"]["value"]  # общее кол-во записей
        items = [hit["_source"] for hit in result["hits"]["hits"]]
        return items, total

    async def create(self, doc_id: str, body: dict) -> dict:
        return await self.client.index(index=self.INDEX, id=doc_id, body=body)

    async def update(self, doc_id: str, body: dict) -> dict:
        try:
            await self.client.update(index=self.INDEX, id=doc_id, body={"doc": body})
            return await self.get_by_id(doc_id)
        except NotFoundError:
            raise ObjectNotFoundException

    async def delete(self, doc_id: str) -> dict:
        try:
            return await self.client.delete(index=self.INDEX, id=doc_id)
        except NotFoundError:
            raise ObjectNotFoundException