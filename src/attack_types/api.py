from fastapi import APIRouter, Depends
from src.dependencies import DBDep, EditorUserDep
from src.attack_types.schemas import (
    AttackApiResponseSchema,
    AttackGroupsQueryParams,
    AttackGroupsResponseSchema,
    AttackTypeCreateSchema,
    AttackTypeDeleteResponseSchema,
    AttackTypeResponseSchema,
    AttackTypeUpdateSchema,
)
from src.exceptions.schemas import error_responses
from src.services.attack_types import AttackTypesService
from src.services.reference_service import ReferenceService
from typing import Annotated


router = APIRouter(prefix="/attack-types", tags=["Attack types"])


QueryParams = Annotated[AttackGroupsQueryParams, Depends(AttackGroupsQueryParams)]


@router.get("/", response_model=AttackApiResponseSchema, summary="Справочник типов атак")
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


@router.post("/", response_model=AttackTypeResponseSchema, status_code=201, summary="Добавить тип атаки",
             responses=error_responses(400, 401, 403, 409))
async def post_attack_type(
        db: DBDep,
        user: EditorUserDep,
        data: AttackTypeCreateSchema
):
    """Прокси POST /reference/attack-types движка; повторный `value` — 409."""
    return await ReferenceService(db).create_attack_type(data=data)


@router.put("/{value}", response_model=AttackTypeResponseSchema, summary="Изменить тип атаки",
            responses=error_responses(401, 403, 404))
async def put_attack_type(
        db: DBDep,
        user: EditorUserDep,
        value: str,
        data: AttackTypeUpdateSchema
):
    """Меняются только `label` и `description`; системные типы изменить нельзя (403)."""
    return await ReferenceService(db).update_attack_type(value=value, data=data)


@router.delete("/{value}", response_model=AttackTypeDeleteResponseSchema, summary="Удалить тип атаки",
               responses=error_responses(401, 403))
async def delete_attack_type(
        db: DBDep,
        user: EditorUserDep,
        value: str
):
    """Удалить можно только добавленный вручную тип; системные — нельзя (403)."""
    return await ReferenceService(db).delete_attack_type(value=value)
