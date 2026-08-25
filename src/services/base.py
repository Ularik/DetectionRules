from src.utils.db_manager import DbManager
from src.utils.elastic_manager import ElasticManager


class BaseService:

    def __init__(self, db: DbManager):
        self.db = db
        self.es = ElasticManager()