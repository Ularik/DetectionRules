from src.connectors.elastic_connector import ElasticConnector
from src.config import settings

elastic_manager = ElasticConnector(host=settings.ES_HOST,
                                 user=settings.ES_USER,
                                 password=settings.ES_PASSWORD,
                                 verify_certs=settings.ES_VERIFY_CERTS)
