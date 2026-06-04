from src.repositories.elastic.base import ElasticRepository


class ElasticRulesRepository(ElasticRepository):
    INDEX = "soc-detection-rules"

    async def search_rules(self, text: str | None = None, limit: int = 10, offset: int = 0) -> dict:
        must = []

        if text:
            must.append({
                "multi_match": {
                    "query": text,
                    "fields": ["pattern", "description"],
                    "type": "best_fields",
                    "fuzziness": "AUTO"  # допускает опечатки
                }
            })

        query = {
                "from": offset,
                "size": limit,
                "query": {"match_all": {}}}
        if must:
            query['query'] = {
                    "bool": {
                        "must": must,
                    }
                }

        items, total = await self.search(query)
        result = {
            "total": total,
            "has_next": total > limit + offset,
            "items": items,
        }
        return result
