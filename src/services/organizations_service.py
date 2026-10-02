from src.organizations.schemas import OrganizationListApiResponse, Organization, AgentsApiResponseSchema, OrganizationCreateApiResponseSchema
from src.services.base import BaseService
from src.organizations.schemas import OrganizationCreateUpdateSchema


class OrganizationService(BaseService):

    async def get_organizations(self):
        res = await self.main_backend.get("/organizations")
        return OrganizationListApiResponse.model_validate(res)

    async def get_organization_detail(self, id: str):
        res = await self.main_backend.get(f"/organizations/{id}")
        return Organization.model_validate(res)

    async def post_organization(self, data: OrganizationCreateUpdateSchema):
        res = await self.main_backend.post("/organizations", data=data)
        return OrganizationCreateApiResponseSchema.model_validate(res)

    async def put_organization(self, org_id: str, data: OrganizationCreateUpdateSchema):
        res = await self.main_backend.put(f"/organizations/{org_id}", data=data)
        return OrganizationCreateApiResponseSchema.model_validate(res)

    async def del_organization(self, org_id: str):
        await self.main_backend.delete(f"/organizations/{org_id}")


    async def get_agents(self):
        res = await self.main_backend.get("/reference/wazuh-agents")
        return AgentsApiResponseSchema.model_validate(res).items