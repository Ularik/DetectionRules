from fastapi import APIRouter
from src.dependencies import DBDep, AuthUserDep
from src.exceptions.schemas import error_responses
from src.rules.schemas import RuleRequestCreateUpdateSchema, RuleESSchema
from src.services.rules_services import RuleService


router = APIRouter(prefix="/analyst", tags=["Правила аналитика"])


@router.post("/", response_model=RuleESSchema, responses=error_responses(400, 503))
async def create_rule(
        db: DBDep,
        data: RuleRequestCreateUpdateSchema,
        user: AuthUserDep
        ):
    new_rule = await RuleService(db).create_rule(user=user, data=data)
    return new_rule

@router.put("/{rule_id}", response_model=RuleESSchema, responses=error_responses(404, 503))
async def update_rule(
        db: DBDep,
        rule_id: str,
        data: RuleRequestCreateUpdateSchema,
        user: AuthUserDep
        ):
    new_rule = await RuleService(db).update_rule(user=user, rule_id=rule_id, data=data)
    return new_rule
