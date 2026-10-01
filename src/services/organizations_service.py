from src.organizations.schemas import OrganizationListApiResponse
from src.services.base import BaseService


class OrganizationService(BaseService):

    async def get_organizations(self):
        res = await self.main_backend.get("/organizations")
        return OrganizationListApiResponse.model_validate(res)