from fastapi import APIRouter

from src.dependencies import AuthUserDep, DBDep, EditorUserDep
from src.exceptions.schemas import error_responses
from src.rule_folders.schemas import (
    RuleFolderAssignmentSchema,
    RuleFolderAssignmentsResponseSchema,
    RuleFolderAssignResponseSchema,
    RuleFolderCreateSchema,
    RuleFolderDeleteResponseSchema,
    RuleFolderListResponseSchema,
    RuleFolderResponseSchema,
    RuleFolderRulesResponseSchema,
)
from src.services.rule_folders_service import RuleFoldersService


router = APIRouter(prefix="/detection-rule-folders", tags=["Папки правил обнаружения"])


@router.get("/", response_model=RuleFolderListResponseSchema, summary="Список папок правил",
            responses=error_responses(401))
async def get_folders(
        db: DBDep,
        user: AuthUserDep,
):
    return await RuleFoldersService(db).get_folders()


@router.get("/assignments", response_model=RuleFolderAssignmentsResponseSchema,
            summary="Привязки правил к папкам", responses=error_responses(401))
async def get_assignments(
        db: DBDep,
        user: AuthUserDep,
):
    """Только правила, лежащие в папках; правила без папки в список не входят."""
    return await RuleFoldersService(db).get_assignments()


@router.post("/", response_model=RuleFolderResponseSchema, status_code=201, summary="Создать папку",
             responses=error_responses(401, 403, 409))
async def post_folder(
        db: DBDep,
        user: EditorUserDep,
        data: RuleFolderCreateSchema,
):
    """Название уникально (1–120 символов); повторное — 409. `folder_id` генерирует движок."""
    return await RuleFoldersService(db).create_folder(data=data)


@router.put("/rules/{rule_id}", response_model=RuleFolderAssignResponseSchema,
            summary="Переместить правило в папку", responses=error_responses(401, 403, 404))
async def put_rule_folder(
        db: DBDep,
        user: EditorUserDep,
        rule_id: str,
        data: RuleFolderAssignmentSchema,
):
    """Прокси PUT /detection-rules/{rule_id}/folder; `folder_id: null` убирает правило из папки."""
    return await RuleFoldersService(db).assign_rule(rule_id=rule_id, data=data)


@router.get("/{folder_id}/rules", response_model=RuleFolderRulesResponseSchema, summary="Правила в папке",
            responses=error_responses(401, 404))
async def get_folder_rules(
        db: DBDep,
        user: AuthUserDep,
        folder_id: str,
):
    return await RuleFoldersService(db).get_folder_rules(folder_id=folder_id)


@router.put("/{folder_id}", response_model=RuleFolderResponseSchema, summary="Переименовать папку",
            responses=error_responses(401, 403, 404, 409))
async def put_folder(
        db: DBDep,
        user: EditorUserDep,
        folder_id: str,
        data: RuleFolderCreateSchema,
):
    return await RuleFoldersService(db).update_folder(folder_id=folder_id, data=data)


@router.delete("/{folder_id}", response_model=RuleFolderDeleteResponseSchema, summary="Удалить папку",
               responses=error_responses(401, 403, 404, 409))
async def delete_folder(
        db: DBDep,
        user: EditorUserDep,
        folder_id: str,
):
    """Удалить можно только пустую папку; иначе 409 со списком правил в ней."""
    return await RuleFoldersService(db).delete_folder(folder_id=folder_id)
