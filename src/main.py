from fastapi import FastAPI
import logging
from contextlib import asynccontextmanager
from src.init import elastic_manager
from src.rules.api import router as rules_router
from fastapi.middleware.cors import CORSMiddleware

logging.basicConfig(level=logging.INFO)

@asynccontextmanager
async def lifespan(app: FastAPI):
    await elastic_manager.connect()
    yield
    await elastic_manager.close()

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(rules_router)