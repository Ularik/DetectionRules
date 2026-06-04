from fastapi import APIRouter, HTTPException

from src.rules.models import SeverityHintEnum
from src.services.rules_services import RuleService
from src.exceptions import ObjectNotFoundException, UniqueObjIsExistException
from src.rules.dependencies import DBDep, PaginationDep, ElasticDep
from src.rules.schemas import RuleCreateUpdateSchema, RuleOutSchema, RulePatchSchema

router = APIRouter(prefix="/rules", tags=["Правила"])


@router.post("/")
async def create_rule(
        db: DBDep,
        elasticdb: ElasticDep,
        data: RuleCreateUpdateSchema,
        ):
    new_rule = await RuleService(db, elasticdb).create_rule(rule_id=data.rule_id, data=data)
    return new_rule


@router.put("/{rule_id}")
async def put_rule(
        rule_id: str,
        elasticdb: ElasticDep,
        db: DBDep,
        data: RuleCreateUpdateSchema
        ):
    try:
        rule = await RuleService(db, elasticdb).update_rule(rule_id=rule_id, data=data)
    except ObjectNotFoundException as err:
        raise HTTPException(status_code=404, detail=err.detail)
    return rule


@router.patch("/{rule_id}", description="Вклюить/Отключить правило")
async def patch_rule(
        rule_id: str,
        elasticdb: ElasticDep,
        db: DBDep,
        data: RulePatchSchema
        ):
    try:
        rule = await RuleService(db, elasticdb).update_rule(rule_id=rule_id, data=data, exclude_unset=True)
    except ObjectNotFoundException as err:
        raise HTTPException(status_code=404, detail=err.detail)
    return rule

@router.get("/")
async def get_rules(
        db: DBDep,
        elasticdb: ElasticDep,
        paging: PaginationDep,
        pattern: str = None,
        rule_id: str = None,
        description: str = None,
        ):
    return await RuleService(db, elasticdb).find_rules(pattern, description, rule_id, limit=paging.limit, offset=paging.offset)


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


@router.delete("/{rule_id}")
async def delete(
        rule_id: str,
        db: DBDep,
        elasticdb: ElasticDep,
        ):
    try:
        return await RuleService(db, elasticdb).delete(rule_id=rule_id)
    except ObjectNotFoundException as err:
        raise HTTPException(status_code=404, detail=err.detail)


@router.get("/enums/severity-hints")
def get_severity_hints():
    return [e.value for e in SeverityHintEnum]
