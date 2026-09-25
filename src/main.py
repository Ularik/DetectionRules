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

setup_exceptions(app)