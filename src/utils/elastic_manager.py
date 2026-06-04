from src.init import elastic_manager
from src.repositories.elastic.rule_elastic import ElasticRulesRepository

class ElasticManager:

    def __init__(self):
        self.rulesRepository = ElasticRulesRepository(elastic_manager.client)