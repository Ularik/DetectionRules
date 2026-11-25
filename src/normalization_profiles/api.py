from fastapi import APIRouter
from src.dependencies import DBDep
from src.services.normalization_profiles_service import NormalizationProfileService
from src.normalization_profiles.schemas import NormalizationProfileSchema, NormalizationProfileTestSchema


router = APIRouter(prefix="/normalization-profiles", tags=["Профили нормализации"])


@router.get("/", summary="Получить профили нормализации")
async def get_profiles(
        db: DBDep,
        enabled_only: bool = False,
):
    return await NormalizationProfileService(db).get_profiles(enabled_only=enabled_only)


@router.post("/", status_code=201, summary="Создать профиль нормализации")
async def post_profile(
        db: DBDep,
        data: NormalizationProfileSchema,
):
    return await NormalizationProfileService(db).post_profile(data=data)


@router.get("/fields", summary="Получить каталог полей нормализации")
async def get_fields(
        db: DBDep,
):
    """Внутренние поля SIEM, доступные для настройки mapping."""
    return await NormalizationProfileService(db).get_fields()


@router.post("/test", summary="Проверить mapping без сохранения")
async def test_profile(
        db: DBDep,
        data: NormalizationProfileTestSchema,
):
    """Применяет временный профиль к raw_event и возвращает результат нормализации."""
    return await NormalizationProfileService(db).test_profile(data=data)


@router.get("/{profile_name}", summary="Получить профиль нормализации")
async def get_profile(
        db: DBDep,
        profile_name: str,
):
    return await NormalizationProfileService(db).get_profile(profile_name=profile_name)


@router.put("/{profile_name}", summary="Изменить профиль нормализации")
async def put_profile(
        db: DBDep,
        profile_name: str,
        data: NormalizationProfileSchema,
):
    return await NormalizationProfileService(db).put_profile(profile_name=profile_name, data=data)


@router.delete("/{profile_name}", summary="Удалить профиль нормализации")
async def delete_profile(
        db: DBDep,
        profile_name: str,
):
    """Системные generic-профили удалить нельзя."""
    return await NormalizationProfileService(db).del_profile(profile_name=profile_name)
