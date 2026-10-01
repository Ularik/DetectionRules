from fastapi import APIRouter, Depends
from src.dependencies import DBDep
from src.scenarios.schema import ScenarioQueryParams
from typing import Annotated
from src.services.scenarios_service import ScenariosService


SParamsDep = Annotated[ScenarioQueryParams, Depends(ScenarioQueryParams)]

router = APIRouter(prefix="/scenarios")


@router.get("/")
async def get_scenarios(
        db: DBDep,
        params: SParamsDep
):
    res = await ScenariosService(db).get_scenarios(query_params=params)
    return res