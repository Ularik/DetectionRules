from fastapi import FastAPI
import logging
from contextlib import asynccontextmanager
from src.init import elastic_manager

logging.basicConfig(level=logging.INFO)

@asynccontextmanager
async def lifespan(app: FastAPI):
    await elastic_manager.connect()
    yield
    await elastic_manager.close()

from src.rules.api import router as rules_router

app = FastAPI(lifespan=lifespan)

app.include_router(rules_router)