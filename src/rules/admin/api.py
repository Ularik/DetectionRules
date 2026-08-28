from fastapi import APIRouter
from src.dependencies import DBDep, AuthUserDep
from src.rules.schemas import RuleRequestCreateUpdateSchema
from src.services.rules_services import RuleService

router = APIRouter(prefix="/admin", tags=["Админские правила"])


@router.post("/")
async def create_rule(
        db: DBDep,
        data: RuleRequestCreateUpdateSchema,
        user: AuthUserDep
        ):
    new_rule = await RuleService(db).create_rule(user=user, data=data)
    return new_rule


@router.put("/{rule_id}")
async def update_rule(
        db: DBDep,
        rule_id: str,
        data: RuleRequestCreateUpdateSchema,
        user: AuthUserDep
        ):
    new_rule = await RuleService(db).update_rule(user=user, rule_id=rule_id, data=data)
    return new_rule

@router.delete("/{rule_id}")
async def delete_rule(
        db: DBDep,
        rule_id: str
):
    res = await RuleService(db).delete(rule_id=rule_id)
    return res