from fastapi import APIRouter, Depends, Body
from src.dependencies import DBDep
from src.incidents.schemas import IncidentParams, UpdateAnalystStatusSchema
from typing import Annotated
from src.services.incident_service import IncidentService


QueryParams = Annotated[IncidentParams, Depends(IncidentParams)]


router = APIRouter(prefix="/incidents")


@router.get("/")
async def get_incidents(
        db: DBDep,
        params: QueryParams
):
    result = await IncidentService(db).get_incidents(params)
    return result


@router.get("/{inc_id}")
async def get_incident_detail(
        db: DBDep,
        inc_id: str
):
    result = await IncidentService(db).get_detail_incident(inc_id)
    return result


@router.get("/{inc_id}/events")
async def get_incident_events(
        db: DBDep,
        inc_id: str,
        page: int = 1,
        size: int = 10
):
    result = await IncidentService(db).get_incident_events(inc_id, page=page, size=size)
    return result


@router.patch("/{inc_id}/status")
async def patch_inc(
        db: DBDep,
        inc_id: str,
        payload: UpdateAnalystStatusSchema = Body(...)
):
    await IncidentService(db).patch_incident(inc_id, payload.analyst_status)
    return {"status": "success", "incident_id": inc_id}
