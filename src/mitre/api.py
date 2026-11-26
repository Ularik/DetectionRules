from fastapi import APIRouter
from src.dependencies import DBDep
from src.mitre.schemas import MitreTacticsResponseSchema
from src.services.mitre_service import MitreService


router = APIRouter(prefix="/mitre", tags=["MITRE"])


@router.get("/mitre")
async def get_technique(
        db: DBDep
):
    return await MitreService(db).get_technique()


@router.get("/tactics", response_model=MitreTacticsResponseSchema, summary="Справочник тактик MITRE ATT&CK")
async def get_tactics(
        db: DBDep
):
    """Прокси /reference/mitre-tactics движка; `value` передаётся в `mitre_tactic` папки корреляции."""
    return await MitreService(db).get_tactics()


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