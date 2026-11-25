from fastapi import FastAPI
import logging
from contextlib import asynccontextmanager
from src.connectors.backend_api_connector import backend_api
from src.init import elastic_manager
from src.rules.api import router as rules_router
from src.users.api import router as users_router
from src.audit.api import router as audit_router
from src.ioc.api import router as ioc_router
from src.supersession_rules.api import router as super_router
from src.correlation_rules.api import router as c_router
from src.incidents.api import router as inc_router
from src.scenarios.api import router as scenario_router
from src.organizations.api import router as org_router
from src.attack_types.api import router as attack_router
from src.events.api import router as event_router
from src.mitre.api import router as mitre_router
from src.sources.api import router as source_router
from src.normalization_profiles.api import router as normalization_router
from src.data_quality.api import router as data_quality_router
from src.assets.api import router as assets_router
from fastapi.middleware.cors import CORSMiddleware
from src.exceptions.exception_handler import setup_exceptions


logging.basicConfig(level=logging.INFO)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await elastic_manager.connect()
    await backend_api.connect()
    await backend_api.health()
    yield
    await elastic_manager.close()
    await backend_api.close()

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(rules_router, prefix="/api")
app.include_router(users_router, prefix="/api")
app.include_router(audit_router, prefix="/api")
app.include_router(ioc_router, prefix="/api")
app.include_router(super_router, prefix="/api")
app.include_router(c_router, prefix="/api")
app.include_router(scenario_router, prefix="/api")
app.include_router(inc_router, prefix="/api")
app.include_router(org_router, prefix="/api")
app.include_router(attack_router, prefix="/api")
app.include_router(event_router, prefix="/api")
app.include_router(mitre_router, prefix="/api")
app.include_router(source_router, prefix="/api")
app.include_router(normalization_router, prefix="/api")
app.include_router(data_quality_router, prefix="/api")
app.include_router(assets_router, prefix="/api")

setup_exceptions(app)