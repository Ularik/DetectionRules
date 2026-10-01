from fastapi import APIRouter, Depends
from typing import Annotated
from src.services.event_service import EventService
from src.dependencies import DBDep
from src.events.schema import RawEventsQueryParamsSchema


EventsParamsDep = Annotated[RawEventsQueryParamsSchema, Depends(RawEventsQueryParamsSchema)]

router = APIRouter(prefix="/events")


@router.get("/")
async def get_events(
        db: DBDep,
        params: EventsParamsDep
):
    return await EventService(db).get_events(params=params)