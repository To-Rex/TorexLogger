from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.application.usecases.auth_usecases import AuthUseCases
from app.infrastructure.database.connection import get_db, engine, async_session_maker
from app.infrastructure.database.models import Base
from app.infrastructure.database.repositories import AdminUserRepository
from app.presentation.routes import (
    auth,
    project,
    log_api,
    log_query,
    websocket,
)

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with async_session_maker() as session:
        admin_repo = AdminUserRepository(session)
        auth_usecases = AuthUseCases(admin_repo)
        try:
            await admin_repo.get_by_username(settings.admin_username)
        except Exception:
            await auth_usecases.create_admin_user(
                settings.admin_username, settings.admin_password
            )

    yield


app = FastAPI(
    title="TorexLogger API",
    description="Centralized Logging System",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(project.router)
app.include_router(log_api.router)
app.include_router(log_query.router)
app.include_router(websocket.router)


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host=settings.api_host, port=settings.api_port)