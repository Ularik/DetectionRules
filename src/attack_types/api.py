from fastapi import APIRouter
from src.dependencies import DBDep
from src.services.attack_types import AttackTypesService


router = APIRouter(prefix="/attack-types", tags=["Attack types"])


@router.get("/")
async def get_attack_types(
        db: DBDep,
):
    result = await AttackTypesService(db).get_attack_types()
    return result