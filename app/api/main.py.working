from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import matching

from app.core.config import (
    get_settings,
)

from app.database.database import (
    Base,
    engine,
)

from app.database import models  # noqa: F401


settings = get_settings()


Base.metadata.create_all(
    bind=engine
)


app = FastAPI(
    title="AI Resume Screening API",
    description=(
        "AI-powered resume screening "
        "and job matching API."
    ),
    version="1.0.0",
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=(
        settings.cors_origin_list
    ),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(
    matching.router,
    prefix="/api",
)


@app.get("/health")
def health():

    return {
        "status": "ok",
        "environment": (
            settings.environment
        ),
    }


@app.get("/")
def root():
    return {
        "name": "AI Resume Screening API",
        "status": "running",
        "health": "/health",
        "docs": "/docs"
    }
