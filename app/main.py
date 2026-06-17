from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import chat, contracts, search
from app.config import settings
from app.database import models  # noqa: F401
from app.database.session import Base, engine


def ensure_app_directories() -> None:
    Path(settings.data_dir).mkdir(parents=True, exist_ok=True)
    Path(settings.upload_dir).mkdir(parents=True, exist_ok=True)
    Path(settings.chroma_persist_dir).mkdir(parents=True, exist_ok=True)


ensure_app_directories()

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Contract Intelligence Platform API",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(
    contracts.router,
    prefix="/contracts",
    tags=["Contracts"],
)

app.include_router(
    search.router,
    prefix="/search",
    tags=["Search"],
)

app.include_router(
    chat.router,
    prefix="/chat",
    tags=["Chat"],
)


@app.get("/")
def root():
    return {
        "message": "Contract Intelligence Platform API",
        "status": "running",
    }


@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "database": "sqlite",
        "environment": settings.environment,
    }
