from elasticsearch import AsyncElasticsearch
import ssl

class ElasticConnector:
    def __init__(self, host: str, user: str, password: str, verify_certs: bool):
        self.host = host
        self.user = user
        self.password = password
        self.verify_certs = verify_certs
        self.client = None


    async def connect(self):
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE if not self.verify_certs else ssl.CERT_REQUIRED

        self.client = AsyncElasticsearch(
            hosts=[self.host],
            basic_auth=(self.user, self.password),
            ssl_context=ssl_context,
        )
        info = await self.client.info()
        print(f"✅ Connected: v{info['version']['number']}")

    async def close(self):
        if self.client:
            await self.client.close()

