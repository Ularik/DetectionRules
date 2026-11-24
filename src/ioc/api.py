from fastapi import APIRouter, Depends
from src.ioc.schemas import IocCreateSchema
from src.dependencies import DBDep, get_editor_user
from src.services.ioc_service import IocService
from src.ioc.dependencies import IocQueryDep


router = APIRouter(prefix="/ioc", tags=["Айок"])


@router.post('/', dependencies=[Depends(get_editor_user)])
async def post_ioc(
        db: DBDep,
        data: IocCreateSchema
):
    return await IocService(db).post_ioc(data)


@router.get('/')
async def get_ioc(
        db: DBDep,
        params: IocQueryDep
):
    return await IocService(db).get_ioc(params)


@router.get('/{ioc_id}')
async def get_ioc(
        db: DBDep,
        ioc_id: str
):
    return await IocService(db).get_ioc_detail(ioc_id)

@router.patch('/{ioc_id}', dependencies=[Depends(get_editor_user)])
async def patch_ioc(
        db: DBDep,
        ioc_id: str
):
    return await IocService(db).patch_ioc_detail(ioc_id)