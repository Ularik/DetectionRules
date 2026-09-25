from fastapi import APIRouter
from src.dependencies import DBDep, AuthUserDep
from src.services.supersession_rules import SuperSessionService
from src.supersession_rules.schemas import SuppressionRuleUpdateSchema, SuppressionRequestPostSchema


router = APIRouter(prefix="/supersession-rules")


@router.get("/")
async def get_rules(
        db: DBDep,
):
    return await SuperSessionService(db).get_supersets()


@router.post("/")
async def post_rule(
        db: DBDep,
        data: SuppressionRequestPostSchema
):
    return await SuperSessionService(db).post_rule(data)



@router.get("/suppression-match-fields")
async def get_match_fields(
        db: DBDep,
):
    return await SuperSessionService(db).get_supersets_match_fields()


@router.get("/{super_id}")
async def get_detail(
        db: DBDep,
        super_id: str
):
    return await SuperSessionService(db).get_detail_superset(super_id=super_id)


@router.put("/{super_id}")
async def put_detail(
        db: DBDep,
        super_id: str,
        data: SuppressionRuleUpdateSchema
):
    return await SuperSessionService(db).put_superset(super_id=super_id, data=data)