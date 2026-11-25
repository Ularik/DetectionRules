from fastapi import APIRouter, Query
from src.dependencies import DBDep
from src.services.data_quality_service import DataQualityService


router = APIRouter(prefix="/data-quality", tags=["Качество данных"])

HoursQuery = Query(default=24, ge=1, description="Период, часов")


@router.get("/summary", summary="Получить сводку качества нормализации")
async def get_summary(
        db: DBDep,
        hours: int = HoursQuery,
        organization_id: str | None = None,
        source_id: str | None = None,
        profile_name: str | None = None,
):
    """Агрегированная статистика Data Quality за период: количество good/warning/error событий,
    проценты, среднее покрытие mapping, частые отсутствующие поля и ошибки парсинга."""
    return await DataQualityService(db).get_summary(
        hours=hours, organization_id=organization_id, source_id=source_id, profile_name=profile_name,
    )


@router.get("/sources", summary="Получить качество нормализации по источникам")
async def get_sources(
        db: DBDep,
        hours: int = HoursQuery,
        organization_id: str | None = None,
        profile_name: str | None = None,
):
    """Data Quality отдельно по каждому источнику: объём событий, good/warning/error,
    проценты ошибок, средний coverage, top missing fields и parse errors."""
    return await DataQualityService(db).get_sources(
        hours=hours, organization_id=organization_id, profile_name=profile_name,
    )


@router.get("/sources/{source_id}", summary="Получить качество конкретного источника")
async def get_source(
        db: DBDep,
        source_id: str,
        hours: int = HoursQuery,
        organization_id: str | None = None,
        profile_name: str | None = None,
):
    """Подробная статистика качества нормализации одного источника за период;
    можно ограничить конкретным профилем нормализации."""
    return await DataQualityService(db).get_source(
        source_id=source_id, hours=hours, organization_id=organization_id, profile_name=profile_name,
    )
