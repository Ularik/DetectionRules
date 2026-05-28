from fastapi import APIRouter, HTTPException

from src.exceptions import ObjectNotFoundException, UniqueObjIsExistException
from src.rules.dependencies import DBDep, PaginationDep
from src.rules.schemas import RuleCreateUpdateSchema, RuleOutSchema


router = APIRouter(prefix="/rules", tags=["Правила"])


@router.post("/")
async def create_rule(
        db: DBDep,
        data: RuleCreateUpdateSchema,
        ) -> RuleOutSchema:
    try:
        new_rule = await db.ruleModel.create_object(data)
    except UniqueObjIsExistException as err:
        raise HTTPException(status_code=400, detail=err.detail)
    await db.save()
    return new_rule


@router.put("/{rule_id}")
async def put_rule(
        rule_id: str,
        db: DBDep,
        data: RuleCreateUpdateSchema
        ) -> RuleOutSchema:
    try:
        rule = await db.ruleModel.put_object(rule_id=rule_id, schema=data)
    except UniqueObjIsExistException as err:
        raise HTTPException(400, detail=err.detail)
    await db.save()
    return rule


@router.patch("/{rule_id}", description="Вклюить/Отключить правило")
async def patch_rule(
        rule_id: str,
        db: DBDep,
        ) -> RuleOutSchema:
    try:
        new_rule = await db.ruleModel.patch_rule(rule_id=rule_id)
    except ObjectNotFoundException as err:
        raise HTTPException(status_code=400, detail=err.detail)
    await db.save()
    return new_rule

@router.get("/")
async def get_rules(
        db: DBDep,
        paging: PaginationDep,
        pattern: str = None,
        rule_id: str = None,
        description: str = None,
        ):
    result, total = await db.ruleModel.get_objects(
        pattern=pattern,
        rule_id=rule_id,
        description=description,
        limit=paging.limit,
        offset=paging.offset
    )

    response = {
        'total': total,
        'limit': paging.limit,
        'offset': paging.offset,
        'is_next': paging.offset + paging.limit <= total,
        'data': result
    }
    return response


@router.get("/{rule_id}")
async def get_one_rule(
        rule_id: str,
        db: DBDep,
        ) -> RuleOutSchema:
    try:
        new_rule = await db.ruleModel.get_one(rule_id=rule_id)
    except ObjectNotFoundException as err:
        raise HTTPException(status_code=404, detail=err.detail)
    await db.save()
    return new_rule