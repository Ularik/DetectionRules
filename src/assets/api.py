from fastapi import APIRouter, Depends
from src.assets.schemas import AssetCreateUpdateSchema, AssetCriticality, AssetType
from src.dependencies import DBDep, get_editor_user
from src.services.assets_service import AssetService


router = APIRouter(prefix="/assets", tags=["Активы"])


@router.get("/", summary="Получить список активов")
async def get_assets(
        db: DBDep,
        enabled_only: bool = False,
        asset_type: AssetType | None = None,
        criticality: AssetCriticality | None = None,
):
    """Asset Inventory SIEM с фильтрами по активности, типу и критичности."""
    return await AssetService(db).get_assets(
        enabled_only=enabled_only, asset_type=asset_type, criticality=criticality,
    )


@router.post("/", status_code=201, summary="Создать актив", dependencies=[Depends(get_editor_user)])
async def post_asset(
        db: DBDep,
        data: AssetCreateUpdateSchema,
):
    """asset_id генерируется внешним API автоматически."""
    return await AssetService(db).post_asset(data=data)


@router.get("/{asset_id}", summary="Получить карточку актива")
async def get_asset(
        db: DBDep,
        asset_id: str,
):
    return await AssetService(db).get_asset(asset_id=asset_id)


@router.put("/{asset_id}", summary="Изменить актив", dependencies=[Depends(get_editor_user)])
async def put_asset(
        db: DBDep,
        asset_id: str,
        data: AssetCreateUpdateSchema,
):
    """Полное обновление актива; asset_id изменить нельзя."""
    return await AssetService(db).put_asset(asset_id=asset_id, data=data)


@router.delete("/{asset_id}", summary="Удалить актив", dependencies=[Depends(get_editor_user)])
async def delete_asset(
        db: DBDep,
        asset_id: str,
):
    return await AssetService(db).del_asset(asset_id=asset_id)
