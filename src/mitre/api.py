from fastapi import APIRouter
from src.dependencies import DBDep
from src.services.mitre_service import MitreService


router = APIRouter(prefix="/mitre")


@router.get("/mitre")
async def get_technique(
        db: DBDep
):
    return await MitreService(db).get_technique()


@router.post("/sync-mitre")
async def sync_technique(
        db: DBDep
):
    return await MitreService(db).sync_directory()