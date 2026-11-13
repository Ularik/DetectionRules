from fastapi import APIRouter, Depends
from src.dependencies import DBDep
from src.attack_types.schemas import AttackGroupsQueryParams, AttackGroupsResponseSchema
from src.services.attack_types import AttackTypesService
from typing import Annotated


router = APIRouter(prefix="/attack-types", tags=["Attack types"])


QueryParams = Annotated[AttackGroupsQueryParams, Depends(AttackGroupsQueryParams)]


@router.get("/")
async def get_attack_types(
        db: DBDep,
):
    result = await AttackTypesService(db).get_attack_types()
    return result


@router.get("/attach-group", response_model=AttackGroupsResponseSchema)
async def get_attack_groups(
        db: DBDep,
        source_ip: str,
        params: QueryParams
):
    result = await AttackTypesService(db).get_attack_groups(source_ip=source_ip, params=params)
    return result
