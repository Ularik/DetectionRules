from fastapi import APIRouter, Depends
from src.dependencies import DBDep
from src.scenarios.schema import (
    ScenarioAggregateSchema,
    ScenarioApiResponse,
    ScenarioEventsParams,
    ScenarioQueryParams,
    ScenariosEventsApiResponseSchema,
)
from typing import Annotated
from src.services.scenarios_service import ScenariosService


SParamsDep = Annotated[ScenarioQueryParams, Depends(ScenarioQueryParams)]
SEventsParams = Annotated[ScenarioEventsParams, Depends(ScenarioEventsParams)]

router = APIRouter(prefix="/scenarios", tags=["Сценарии"])


@router.get("/", response_model=ScenarioApiResponse)
async def get_scenarios(
        db: DBDep,
        params: SParamsDep
):
    res = await ScenariosService(db).get_scenarios(query_params=params)
    return res


@router.get("/{id}", response_model=ScenarioAggregateSchema)
async def get_scenario_detail(
    db: DBDep,
    id: str
):
    return await ScenariosService(db).get_detail_scenario(scenario_id=id)


@router.get("/{id}/events", response_model=ScenariosEventsApiResponseSchema)
async def get_scenario_events(
    db: DBDep,
    id: str,
    params: SEventsParams
):
    return await ScenariosService(db).get_scenario_events(scenario_id=id, params=params)