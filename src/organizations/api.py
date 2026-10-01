from fastapi import APIRouter, Depends
from src.dependencies import DBDep
from src.services.organizations_service import OrganizationService


router = APIRouter(prefix="/organizations")


@router.get("/")
async def get_organizations(
        db: DBDep,
):
    result = await OrganizationService(db).get_organizations()
    return result