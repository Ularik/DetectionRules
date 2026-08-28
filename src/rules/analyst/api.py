from fastapi import APIRouter, HTTPException
from src.dependencies import DBDep, AuthUserDep
from src.exceptions.exceptions import RuleAlreadyExistException
from src.rules.schemas import RuleRequestCreateUpdateSchema
from src.services.rules_services import RuleService


router = APIRouter(prefix="/analyst", tags=["Правила аналитика"])


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
    pass
