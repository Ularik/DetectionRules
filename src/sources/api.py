from fastapi import APIRouter, Query
from src.dependencies import DBDep
from src.services.sources_service import SourceService
from src.sources.schemas import SourceCreateUpdateSchema


router = APIRouter(prefix="/sources", tags=["Источники"])


@router.get("/")
async def get_sources(
        db: DBDep,
):
    return await SourceService(db).get_sources()


@router.post("/", status_code=201)
async def post_source(
        db: DBDep,
        data: SourceCreateUpdateSchema,
):
    return await SourceService(db).post_source(data=data)


@router.get("/{source_id}/health", summary="Получить состояние источника")
async def get_source_health(
        db: DBDep,
        source_id: str,
):
    """Текущее состояние источника по поступлению событий в Wazuh Elasticsearch:
    время последнего события, количество событий за 5 минут, средний EPS, задержка и статус."""
    return await SourceService(db).get_source_health(source_id=source_id)


@router.get("/{source_id}/sample-events", summary="Получить примеры raw-событий источника")
async def get_source_sample_events(
        db: DBDep,
        source_id: str,
        size: int = Query(default=5, ge=1),
):
    """Последние raw-события источника из индексов Wazuh Elasticsearch
    (для настройки Normalization Profile)."""
    return await SourceService(db).get_source_sample_events(source_id=source_id, size=size)


@router.get("/{source_id}")
async def get_source_detail(
        db: DBDep,
        source_id: str,
):
    return await SourceService(db).get_source_detail(source_id=source_id)


@router.put("/{source_id}")
async def put_source(
        db: DBDep,
        source_id: str,
        data: SourceCreateUpdateSchema,
):
    return await SourceService(db).put_source(source_id=source_id, data=data)


@router.delete("/{source_id}")
async def delete_source(
        db: DBDep,
        source_id: str,
):
    return await SourceService(db).del_source(source_id=source_id)
