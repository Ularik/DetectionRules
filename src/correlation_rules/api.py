from fastapi import APIRouter
from src.services.correlation_rules_service import CorrelationRuleService
from src.services.reference_service import ReferenceService
from src.dependencies import DBDep, AuthUserDep
from src.correlation_rules.schemas import CorrelationRuleRequestCreateUpdateSchema


router = APIRouter(prefix="/correlation-rules")


@router.get("/")
async def get_crules(
        db: DBDep,
        user: AuthUserDep
):
    result = await CorrelationRuleService(db).get_crules()
    return result


@router.get("/sequence")
async def get_sequence(
        db: DBDep
):
    result = await ReferenceService(db).get_sequence_types()
    return result


@router.get("/group-by-fields")
async def get_group_by_fields(
        db: DBDep
):
    result = await ReferenceService(db).get_group_by_fields()
    return result


@router.get("/{correlation_id}")
async def get_crules(
        db: DBDep,
        user: AuthUserDep,
        correlation_id: str
):
    result = await CorrelationRuleService(db).get_crule_detail(correlation_id=correlation_id)
    return result


@router.post("/")
async def post_crule(
        db: DBDep,
        user: AuthUserDep,
        data: CorrelationRuleRequestCreateUpdateSchema
):
    result = await CorrelationRuleService(db).create_crule(data=data, user=user)
    return result


@router.put("/{correlation_id}")
async def put_crule(
        db: DBDep,
        correlation_id: str,
        user: AuthUserDep,
        data: CorrelationRuleRequestCreateUpdateSchema
):
    result = await CorrelationRuleService(db).put_crule(data=data, user=user, correlation_id=correlation_id)
    return result
