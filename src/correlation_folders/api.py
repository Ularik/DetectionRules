from fastapi import APIRouter

from src.correlation_folders.schemas import (
    CorrelationFolderAssignmentSchema,
    CorrelationFolderAssignmentsResponseSchema,
    CorrelationFolderAssignResponseSchema,
    CorrelationFolderCreateSchema,
    CorrelationFolderDeleteResponseSchema,
    CorrelationFolderListResponseSchema,
    CorrelationFolderResponseSchema,
    CorrelationFolderRulesResponseSchema,
)
from src.dependencies import AuthUserDep, DBDep, EditorUserDep
from src.exceptions.schemas import error_responses
from src.services.correlation_folders_service import CorrelationFoldersService


router = APIRouter(prefix="/correlation-folders", tags=["Папки правил корреляции"])


@router.get("/", response_model=CorrelationFolderListResponseSchema, summary="Список папок правил корреляции",
            responses=error_responses(401))
async def get_folders(
        db: DBDep,
        user: AuthUserDep,
):
    return await CorrelationFoldersService(db).get_folders()


@router.get("/assignments", response_model=CorrelationFolderAssignmentsResponseSchema,
            summary="Привязки правил корреляции к папкам", responses=error_responses(401))
async def get_assignments(
        db: DBDep,
        user: AuthUserDep,
):
    """Только правила, лежащие в папках; остальные показываются в разделе «Без папки»."""
    return await CorrelationFoldersService(db).get_assignments()


@router.post("/", response_model=CorrelationFolderResponseSchema, status_code=201, summary="Создать папку",
             responses=error_responses(401, 403, 409))
async def post_folder(
        db: DBDep,
        user: EditorUserDep,
        data: CorrelationFolderCreateSchema,
):
    """Название уникально внутри тактики MITRE (повторное — 409). `folder_id` генерирует движок."""
    return await CorrelationFoldersService(db).create_folder(data=data)


@router.put("/rules/{correlation_id}", response_model=CorrelationFolderAssignResponseSchema,
            summary="Переместить правило корреляции в папку", responses=error_responses(401, 403, 404))
async def put_rule_folder(
        db: DBDep,
        user: EditorUserDep,
        correlation_id: str,
        data: CorrelationFolderAssignmentSchema,
):
    """Прокси PUT /correlation-rules/{correlation_id}/folder; `folder_id: null` убирает правило из папки.
    Само правило не меняется."""
    return await CorrelationFoldersService(db).assign_rule(correlation_id=correlation_id, data=data)


@router.get("/{folder_id}/rules", response_model=CorrelationFolderRulesResponseSchema,
            summary="Правила в папке", responses=error_responses(401, 404))
async def get_folder_rules(
        db: DBDep,
        user: AuthUserDep,
        folder_id: str,
):
    """Только идентификаторы правил; сами правила — GET /api/correlation-rules."""
    return await CorrelationFoldersService(db).get_folder_rules(folder_id=folder_id)


@router.put("/{folder_id}", response_model=CorrelationFolderResponseSchema,
            summary="Переименовать папку или сменить тактику", responses=error_responses(401, 403, 404, 409))
async def put_folder(
        db: DBDep,
        user: EditorUserDep,
        folder_id: str,
        data: CorrelationFolderCreateSchema,
):
    """Оба поля обязательны; привязанные правила остаются в папке."""
    return await CorrelationFoldersService(db).update_folder(folder_id=folder_id, data=data)


@router.delete("/{folder_id}", response_model=CorrelationFolderDeleteResponseSchema, summary="Удалить папку",
               responses=error_responses(401, 403, 404, 409))
async def delete_folder(
        db: DBDep,
        user: EditorUserDep,
        folder_id: str,
):
    """Удалить можно только пустую папку, иначе 409 со списком правил. Правила не удаляются."""
    return await CorrelationFoldersService(db).delete_folder(folder_id=folder_id)
