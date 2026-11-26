from contextlib import asynccontextmanager

import aiohttp
from fastapi import HTTPException, status

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
from src.services.base import BaseService


@asynccontextmanager
async def folder_errors_guard(
        not_found: str = "Папка не найдена",
        conflict: str = "Папка с таким названием уже существует",
):
    """Понятные тексты ошибок движка вместо общих сообщений обработчика (папки правил обнаружения и корреляции).

    Движок отвечает 404 на несуществующую папку (и правило при привязке),
    409 — на повторное название папки (на DELETE — на непустую папку, это обрабатывает сервис).
    """
    try:
        yield
    except aiohttp.ClientResponseError as err:
        if err.status == status.HTTP_404_NOT_FOUND:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=not_found) from err
        if err.status == status.HTTP_409_CONFLICT:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=conflict,
            ) from err
        raise


class RuleFoldersService(BaseService):
    """Прокси /detection-rule-folders внешнего API (папки правил обнаружения)"""

    async def get_folders(self) -> RuleFolderListResponseSchema:
        res = await self.main_backend.get("/detection-rule-folders")
        return RuleFolderListResponseSchema.model_validate(res)

    async def get_assignments(self) -> RuleFolderAssignmentsResponseSchema:
        res = await self.main_backend.get("/detection-rule-folders/assignments")
        return RuleFolderAssignmentsResponseSchema.model_validate(res)

    async def get_folder_rules(self, folder_id: str) -> RuleFolderRulesResponseSchema:
        async with folder_errors_guard():
            res = await self.main_backend.get(f"/detection-rule-folders/{folder_id}/rules")
        return RuleFolderRulesResponseSchema.model_validate(res)

    async def create_folder(self, data: RuleFolderCreateSchema) -> RuleFolderResponseSchema:
        async with folder_errors_guard():
            res = await self.main_backend.post("/detection-rule-folders", data=data)
        return RuleFolderResponseSchema.model_validate(res)

    async def update_folder(self, folder_id: str, data: RuleFolderCreateSchema) -> RuleFolderResponseSchema:
        async with folder_errors_guard():
            res = await self.main_backend.put(f"/detection-rule-folders/{folder_id}", data=data)
        return RuleFolderResponseSchema.model_validate(res)

    async def delete_folder(self, folder_id: str) -> RuleFolderDeleteResponseSchema:
        try:
            async with folder_errors_guard():
                res = await self.main_backend.delete(f"/detection-rule-folders/{folder_id}")
        except HTTPException as exc:
            if exc.status_code != status.HTTP_409_CONFLICT:
                raise
            # 409 на DELETE — папка не пуста; тело ошибки коннектор не отдаёт, поэтому правила запрашиваем отдельно
            rules = await self.get_folder_rules(folder_id=folder_id)
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Папка не пуста, сначала перенесите или уберите из неё правила: " + ", ".join(rules.rule_ids),
            ) from exc
        return RuleFolderDeleteResponseSchema.model_validate(res)

    async def assign_rule(self, rule_id: str, data: RuleFolderAssignmentSchema) -> RuleFolderAssignResponseSchema:
        async with folder_errors_guard(not_found="Правило или папка не найдены"):
            res = await self.main_backend.put(f"/detection-rules/{rule_id}/folder", data=data)
        return RuleFolderAssignResponseSchema.model_validate(res)
