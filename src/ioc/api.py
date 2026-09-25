from fastapi import APIRouter
from src.ioc.schemas import IocCreateSchema
from src.dependencies import DBDep
from src.services.ioc_service import IocService
from src.ioc.dependencies import IocQueryDep


router = APIRouter(prefix="/ioc")


@router.post('/')
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

@router.patch('/{ioc_id}')
async def patch_ioc(
        db: DBDep,
        ioc_id: str
):
    return await IocService(db).patch_ioc_detail(ioc_id)