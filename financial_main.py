"""Financial API entry point. Run: uvicorn financial_main:app --reload --port 8001."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import models.financial_gold  # noqa: F401  — register Gold tables on Base.metadata
from config.database import Base, engine
from config.settings import settings
from routes import financial_dev, financial_gold


@asynccontextmanager
async def lifespan(_app: FastAPI):
    """Create Gold tables that are not already in the database."""
    Base.metadata.create_all(bind=engine)
    yield
    engine.dispose()


app = FastAPI(title=settings.app_name, version="1.0.0", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(financial_gold.router)
if settings.enable_dev_ingest:
    app.include_router(financial_dev.router)


@app.get("/health")
def health() -> dict[str, str]:
    """Liveness check."""
    return {"status": "ok"}
