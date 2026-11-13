import asyncio
import datetime

from fastapi import HTTPException

from src.incidents.schemas import IncidentParams, IncidentEventResponseSchema, IncidentApiResponse
from src.services.base import BaseService
from src.incidents.schemas import IncidentSchema


class IncidentService(BaseService):

    async def get_incidents(self, params: IncidentParams):
        res = await self.main_backend.get("/hunting/incidents", params=params.model_dump(exclude_none=True))
        return IncidentApiResponse.model_validate(res)

    # Ограничения подсчёта по дням: один запрос к бэкенду на каждый день окна
    DAILY_COUNT_MAX_DAYS = 366
    DAILY_COUNT_CONCURRENCY = 5

    async def get_daily_count_of_incidents(self, params: IncidentParams):
        # По умолчанию — последние 10 дней (UTC)
        if not params.from_time or not params.to_time:
            today = datetime.datetime.now(datetime.timezone.utc).date()
            params.from_time = f"{today - datetime.timedelta(days=9)}T00:00:00"
            params.to_time = f"{today}T23:59:59.999999"

        # Дата без времени в to_time означает весь этот день, а не его полночь
        if "T" not in params.to_time and " " not in params.to_time:
            params.to_time = f"{params.to_time}T23:59:59.999999"

        try:
            start_dt = datetime.datetime.fromisoformat(params.from_time)
            end_dt = datetime.datetime.fromisoformat(params.to_time)
        except ValueError:
            raise HTTPException(status_code=422, detail="from_time и to_time должны быть в формате ISO 8601")

        # Строки без часового пояса считаем UTC; все даты приводим к поясу from_time
        naive = start_dt.tzinfo is None
        tz = start_dt.tzinfo or datetime.timezone.utc
        start_dt = start_dt.replace(tzinfo=tz)
        end_dt = end_dt.replace(tzinfo=end_dt.tzinfo or tz).astimezone(tz)

        if end_dt < start_dt:
            raise HTTPException(status_code=422, detail="to_time должен быть не раньше from_time")
        days_count = (end_dt.date() - start_dt.date()).days + 1
        if days_count > self.DAILY_COUNT_MAX_DAYS:
            raise HTTPException(
                status_code=422,
                detail=f"Период не может быть больше {self.DAILY_COUNT_MAX_DAYS} дней",
            )

        def fmt(dt: datetime.datetime) -> str:
            # Отдаём бэкенду время в том же виде, в каком его прислал фронт (с поясом или без)
            return (dt.replace(tzinfo=None) if naive else dt).isoformat()

        # Бэкенд сам считает total по фильтру — забираем только его, без записей (size=1)
        base_query = params.model_dump(exclude_none=True)
        base_query.update(page=1, size=1)
        semaphore = asyncio.Semaphore(self.DAILY_COUNT_CONCURRENCY)

        async def count_for_day(day: datetime.date) -> dict:
            day_start = datetime.datetime.combine(day, datetime.time.min, tzinfo=tz)
            day_end = datetime.datetime.combine(day, datetime.time.max, tzinfo=tz)
            query = {
                **base_query,
                "from_time": fmt(max(day_start, start_dt)),
                "to_time": fmt(min(day_end, end_dt)),
            }
            async with semaphore:
                res = await self.main_backend.get("/hunting/incidents", params=query)
            return {"date": day.isoformat(), "count": int(res.get("total", 0))}

        days = [start_dt.date() + datetime.timedelta(days=i) for i in range(days_count)]
        return await asyncio.gather(*(count_for_day(day) for day in days))

    async def get_detail_incident(self, inc_id: str):
        res = await self.main_backend.get(f"/hunting/incidents/{inc_id}")
        return IncidentSchema.model_validate(res)

    async def get_incident_events(self, inc_id: str, page: int = 1, size: int = 10):
        res = await self.main_backend.get(f"/hunting/incidents/{inc_id}/events", params={
            "page": page,
            "size": size
        })
        return IncidentEventResponseSchema.model_validate(res)

    async def patch_incident(self, inc_id: str, analyst_status: str):
        await self.main_backend.patch(f"/hunting/incidents/{inc_id}/status", data={"analyst_status": analyst_status})
