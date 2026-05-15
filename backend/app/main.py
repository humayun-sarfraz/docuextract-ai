import logging
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import init_db
from app.routes import documents, extraction, automation
from app.config import FRONTEND_BASE_URL, validate_config

logger = logging.getLogger("docuextract")


def _build_cors_origins() -> list[str]:
    origins = [FRONTEND_BASE_URL]
    extra = os.getenv("CORS_ORIGINS", "")
    if extra:
        origins.extend([o.strip() for o in extra.split(",") if o.strip()])
    return origins


@asynccontextmanager
async def lifespan(app: FastAPI):
    validate_config()
    init_db()
    logger.info("DocuExtract AI started")
    yield
    logger.info("DocuExtract AI shutting down")


app = FastAPI(
    title="DocuExtract AI",
    description="Simple AI Document Data Extractor",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=_build_cors_origins(),
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

app.include_router(documents.router)
app.include_router(extraction.router)
app.include_router(automation.router)


@app.get("/health")
def health():
    return {"status": "ok", "service": "DocuExtract AI"}
