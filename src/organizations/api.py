from fastapi import APIRouter, Depends
from src.dependencies import DBDep
from src.services.organizations_service import OrganizationService
from src.organizations.schemas import OrganizationCreateUpdateSchema


router = APIRouter(prefix="/organizations", tags=["Организации"])


@router.get("/")
async def get_organizations(
        db: DBDep,
):
    result = await OrganizationService(db).get_organizations()
    return result


@router.get("/agents")
async def get_agents(
        db: DBDep,
):
    result = await OrganizationService(db).get_agents()
    return result


@router.get("/{id}")
async def get_organization_detail(
        db: DBDep,
        id: str
):
    result = await OrganizationService(db).get_organization_detail(id=id)
    return result


@router.post("/")
async def post_organization(
        db: DBDep,
        data: OrganizationCreateUpdateSchema
):
    result = await OrganizationService(db).post_organization(data=data)
    return result


@router.put("/{organization_id}")
async def post_organization(
        db: DBDep,
        data: OrganizationCreateUpdateSchema,
        organization_id: str
):
    result = await OrganizationService(db).put_organization(org_id=organization_id, data=data)
    return result


@router.delete("/{organization_id}")
async def delete_organization(
        db: DBDep,
        organization_id: str
):
    result = await OrganizationService(db).del_organization(org_id=organization_id)
    return result

