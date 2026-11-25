from fastapi import APIRouter
from src.dependencies import DBDep, AuthUserDep
from src.exceptions.schemas import error_responses
from src.rules.schemas import RuleRequestCreateUpdateSchema, RuleSetStatusSchema, TestRuleSchema, RuleESSchema, \
    RuleDeleteResponseSchema, TestRuleResponseSchema
from src.services.rules_services import RuleService

router = APIRouter(prefix="/admin", tags=["Админские правила"])


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

@router.delete("/{rule_id}", response_model=RuleDeleteResponseSchema, responses=error_responses(404, 503))
async def delete_rule(
        db: DBDep,
        rule_id: str
):
    res = await RuleService(db).delete(rule_id=rule_id)
    return res

@router.patch("/{rule_id}", response_model=RuleESSchema, responses=error_responses(404, 502, 504))
async def turn_on_rules(
        db: DBDep,
        rule_id: str,
        data: RuleSetStatusSchema
):
    res = await RuleService(db).set_status(rule_id, data)
    return res


@router.post("/test", response_model=TestRuleResponseSchema, responses=error_responses(400, 502, 504))
async def test_rule(
        db: DBDep,
        data: TestRuleSchema,
        user: AuthUserDep
        ):
    res = await RuleService(db).test_rule(data=data)
    return res
