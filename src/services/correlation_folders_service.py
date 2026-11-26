from fastapi import HTTPException, status

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
from src.services.base import BaseService
from src.services.rule_folders_service import folder_errors_guard

_NAME_CONFLICT = "Папка с таким названием уже есть в этой тактике MITRE"


class CorrelationFoldersService(BaseService):
    """Прокси /correlation-folders внешнего API (папки правил корреляции)"""

    async def get_folders(self) -> CorrelationFolderListResponseSchema:
        res = await self.main_backend.get("/correlation-folders")
        return CorrelationFolderListResponseSchema.model_validate(res)

    async def get_assignments(self) -> CorrelationFolderAssignmentsResponseSchema:
        res = await self.main_backend.get("/correlation-folders/assignments")
        return CorrelationFolderAssignmentsResponseSchema.model_validate(res)

    async def get_folder_rules(self, folder_id: str) -> CorrelationFolderRulesResponseSchema:
        async with folder_errors_guard():
            res = await self.main_backend.get(f"/correlation-folders/{folder_id}/rules")
        return CorrelationFolderRulesResponseSchema.model_validate(res)

    async def create_folder(self, data: CorrelationFolderCreateSchema) -> CorrelationFolderResponseSchema:
        async with folder_errors_guard(conflict=_NAME_CONFLICT):
            res = await self.main_backend.post("/correlation-folders", data=data)
        return CorrelationFolderResponseSchema.model_validate(res)

    async def update_folder(self, folder_id: str, data: CorrelationFolderCreateSchema) -> CorrelationFolderResponseSchema:
        async with folder_errors_guard(conflict=_NAME_CONFLICT):
            res = await self.main_backend.put(f"/correlation-folders/{folder_id}", data=data)
        return CorrelationFolderResponseSchema.model_validate(res)

    async def delete_folder(self, folder_id: str) -> CorrelationFolderDeleteResponseSchema:
        try:
            async with folder_errors_guard():
                res = await self.main_backend.delete(f"/correlation-folders/{folder_id}")
        except HTTPException as exc:
            if exc.status_code != status.HTTP_409_CONFLICT:
                raise
            # 409 на DELETE — в папке есть правила; тело ошибки коннектор не отдаёт, поэтому запрашиваем их отдельно
            rules = await self.get_folder_rules(folder_id=folder_id)
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Папка не пуста, сначала перенесите или уберите из неё правила: "
                       + ", ".join(rules.correlation_ids),
            ) from exc
        return CorrelationFolderDeleteResponseSchema.model_validate(res)

    async def assign_rule(self, correlation_id: str,
                          data: CorrelationFolderAssignmentSchema) -> CorrelationFolderAssignResponseSchema:
        async with folder_errors_guard(not_found="Правило корреляции или папка не найдены"):
            res = await self.main_backend.put(f"/correlation-rules/{correlation_id}/folder", data=data)
        return CorrelationFolderAssignResponseSchema.model_validate(res)
