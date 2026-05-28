from src.connectors.elastic_connector import ElasticManager
from src.config import settings

INDEX_ES = "soc-detection-rules"

elastic_manager = ElasticManager(host=settings.ES_HOST,
                                 user=settings.ES_USER,
                                 password=settings.ES_PASSWORD,
                                 verify_certs=settings.ES_VERIFY_CERTS)
