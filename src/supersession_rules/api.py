from fastapi import APIRouter
from src.dependencies import DBDep, AuthUserDep
from src.services.supersession_rules import SuperSessionService
from src.supersession_rules.schemas import SuppressionRuleUpdateSchema, SuppressionRequestPostSchema, \
    SuppressionRuleStatusSchema, SuppressionRuleTestSchema


router = APIRouter(prefix="/supersession-rules", tags=["Супер Правила"])


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


@router.post("/test")
async def test_rule(
        db: DBDep,
        data: SuppressionRuleTestSchema
):
    return await SuperSessionService(db).test_rule(data)


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


@router.delete("/{super_id}")
async def delete_rule(
        db: DBDep,
        super_id: str
):
    return await SuperSessionService(db).delete_rule(super_id=super_id)


@router.patch("/{super_id}/status")
async def set_status(
        db: DBDep,
        super_id: str,
        data: SuppressionRuleStatusSchema
):
    return await SuperSessionService(db).set_status(super_id=super_id, data=data)