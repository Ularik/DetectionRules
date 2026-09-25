from src.correlation_rules.models import CorrelationRuleModel
from src.correlation_rules.schemas import CorrelationRuleDBSchema
from src.repositories.pg.base import BaseRepository


class CorrelationRuleRepository(BaseRepository):
    model = CorrelationRuleModel
    schema = CorrelationRuleDBSchema



