from src.ioc.dependencies import IocQueryDep
from src.services.base import BaseService
from src.ioc.schemas import IocCreateSchema, PaginatedResponse, IocItemSchema, IocItemPatchcSchema
import logging


logger = logging.getLogger(__name__)


class IocService(BaseService):

    async def post_ioc(self, data: IocCreateSchema):
        return await self.main_backend.post(
            '/threat-intel/iocs/publish',
            data=data
        )

    async def get_ioc(self, params: IocQueryDep) -> PaginatedResponse[IocItemSchema]:
        params = params.model_dump(exclude_none=True)
        res = await self.main_backend.get('/threat-intel/iocs', params=params)

        return PaginatedResponse[IocItemSchema].model_validate(res)

    async def get_ioc_detail(self, ioc_id: str) -> IocItemSchema:
        res = await self.main_backend.get(f'/threat-intel/iocs/{ioc_id}')
        return IocItemSchema.model_validate(res)

    async def patch_ioc_detail(self, ioc_id: str) -> IocItemPatchcSchema:
        res = await self.main_backend.patch(f'/threat-intel/iocs/{ioc_id}/viewed')
        return IocItemPatchcSchema.model_validate(res)