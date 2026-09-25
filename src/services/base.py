from src.utils.db_manager import DbManager
from src.utils.elastic_manager import ElasticManager
from src.connectors.backend_api_connector import backend_api


class BaseService:

    def __init__(self, db: DbManager):
        self.db = db
        self.es = ElasticManager()
        self.main_backend = backend_api