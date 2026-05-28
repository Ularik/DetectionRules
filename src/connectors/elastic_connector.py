from elasticsearch import AsyncElasticsearch
import ssl

class ElasticManager:
    def __init__(self, host: str, user: str, password: str, verify_certs: bool):
        self.host = host
        self.user = user
        self.password = password
        self.verify_certs = verify_certs
        self.elastic = None


    async def connect(self):
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE

        self.elastic = AsyncElasticsearch(
            hosts=["https://192.168.100.66:9200"],
            basic_auth=("elastic", "Zv5h+cGGHq_o06_cXfjs"),
            ssl_context=ssl_context,
        )
        info = await self.elastic.info()
        print(f"✅ Connected: v{info['version']['number']}")

    async def get(self, key: str):
        return self.elastic

    async def close(self):
        if self.elastic:
            await self.elastic.close()
