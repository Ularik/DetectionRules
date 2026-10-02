from fastapi import APIRouter, Depends
from typing import Annotated
from src.services.event_service import EventService
from src.dependencies import DBDep
from src.events.schema import RawEventsQueryParamsSchema


EventsParamsDep = Annotated[RawEventsQueryParamsSchema, Depends(RawEventsQueryParamsSchema)]

router = APIRouter(prefix="/events", tags=["События"])


@router.get("/")
async def get_events(
        db: DBDep,
        params: EventsParamsDep
):
    return await EventService(db).get_events(params=params)


@router.get("/{index_name}/{event_id}")
async def get_event_detail(
        db: DBDep,
        index_name: str,
        event_id: str
):
    return await EventService(db).get_event_detail(index_name=index_name, event_id=event_id)