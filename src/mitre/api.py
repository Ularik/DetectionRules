from fastapi import APIRouter
from src.dependencies import DBDep
from src.services.mitre_service import MitreService


router = APIRouter(prefix="/mitre", tags=["MITRE"])


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


# объявлен после статических путей, чтобы не перехватывать /mitre
@router.get("/{mitre_id}")
async def get_technique_detail(
        db: DBDep,
        mitre_id: str
):
    return await MitreService(db).get_technique_detail(mitre_id=mitre_id)