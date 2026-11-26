from fastapi import APIRouter
from src.dependencies import AdminUserDep, AuthUserDep, DBDep, EditorUserDep
from src.engine_settings.schemas import (
    EngineSettingsResponseSchema,
    EngineSettingsSchema,
    EngineSettingsUpdateResponseSchema,
    EngineSettingsValidateResponseSchema,
)
from src.exceptions.schemas import error_responses
from src.services.engine_settings_service import EngineSettingsService


router = APIRouter(
    prefix="/engine-settings",
    tags=["Настройки движка"],
    responses=error_responses(401, 502, 504),
)

# Форма ответа reset взята по аналогии с PUT (на живом движке не проверялась),
# поэтому схема только документируется, а не применяется к ответу
_RESET_DOC = {200: {"model": EngineSettingsUpdateResponseSchema, "description": "Настройки по умолчанию"}}


@router.get("/", summary="Получить настройки движка", response_model=EngineSettingsResponseSchema)
async def get_engine_settings(db: DBDep, user: AuthUserDep):
    """Текущие настройки корреляции, скоринга IOC/активов, порогов решений и трекера атак."""
    return await EngineSettingsService(db).get_settings()


@router.post(
    "/validate",
    summary="Проверить настройки движка",
    response_model=EngineSettingsValidateResponseSchema,
    responses=error_responses(403),
)
async def validate_engine_settings(db: DBDep, user: EditorUserDep, data: EngineSettingsSchema):
    """Проверка настроек движком без сохранения."""
    return await EngineSettingsService(db).validate_settings(data=data, username=user.username)


@router.post("/reset", summary="Сбросить настройки движка", responses={**_RESET_DOC, **error_responses(403)})
async def reset_engine_settings(db: DBDep, user: AdminUserDep):
    """Возврат настроек движка к значениям по умолчанию."""
    return await EngineSettingsService(db).reset_settings()


@router.put(
    "/",
    summary="Изменить настройки движка",
    response_model=EngineSettingsUpdateResponseSchema,
    responses=error_responses(403),
)
async def put_engine_settings(db: DBDep, user: AdminUserDep, data: EngineSettingsSchema):
    """Полная замена настроек. updated_by движок проставляет сам (наше значение игнорирует)."""
    return await EngineSettingsService(db).update_settings(data=data, username=user.username)
