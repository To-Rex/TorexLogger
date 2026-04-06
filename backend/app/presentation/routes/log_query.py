from datetime import datetime
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.usecases.auth_usecases import AuthUseCases
from app.application.usecases.log_usecases import LogUseCases
from app.infrastructure.database.connection import get_db
from app.infrastructure.database.repositories import (
    LogRepository,
    AdminUserRepository,
)
from app.infrastructure.redis.pubsub import RedisPubSub, get_redis_pubsub
from app.presentation.schemas.project import LogListResponse, LogResponse
from app.presentation.routes.auth import verify_token
from app.presentation.routes.project import get_project_usecases
from app.application.usecases.project_usecases import ProjectUseCases

router = APIRouter(prefix="/api/admin/logs", tags=["admin-logs"])
security = HTTPBearer()


async def get_log_usecases(
    session: AsyncSession = Depends(get_db),
    redis_pubsub: RedisPubSub = Depends(get_redis_pubsub),
) -> LogUseCases:
    log_repo = LogRepository(session)
    return LogUseCases(log_repo, redis_pubsub)


async def get_admin_auth_usecases(
    session: AsyncSession = Depends(get_db),
) -> AuthUseCases:
    repo = AdminUserRepository(session)
    return AuthUseCases(repo)


class DeviceListResponse(BaseModel):
    devices: list[str]


@router.get("/devices", response_model=DeviceListResponse, summary="Get device list", description="Retrieve list of unique devices for a project")
async def get_devices(
    project_id: UUID = Query(..., description="Project ID to get devices for"),
    _: str = Depends(verify_token),
    usecases: LogUseCases = Depends(get_log_usecases),
):
    devices = await usecases.get_devices(project_id)
    return DeviceListResponse(devices=devices)


@router.get("", response_model=LogListResponse, summary="Query logs", description="Retrieve logs with optional filtering by project, level, date range, and device")
async def query_logs(
    project_id: Optional[UUID] = Query(None, description="Project ID to filter logs"),
    level: Optional[str] = Query(None, description="Log level to filter (info, warning, error, debug)"),
    start_date: Optional[datetime] = Query(None, description="Start date for filtering logs"),
    end_date: Optional[datetime] = Query(None, description="End date for filtering logs"),
    device: Optional[str] = Query(None, description="Device identifier to filter logs"),
    limit: int = Query(100, ge=1, le=500, description="Maximum number of logs to return"),
    offset: int = Query(0, ge=0, description="Number of logs to skip"),
    _: str = Depends(verify_token),
    usecases: LogUseCases = Depends(get_log_usecases),
):
    if not project_id:
        raise HTTPException(status_code=400, detail="project_id is required")

    logs = await usecases.get_logs(
        project_id=project_id,
        level=level,
        start_date=start_date,
        end_date=end_date,
        device=device,
        limit=limit,
        offset=offset,
    )
    total = await usecases.count_logs(
        project_id=project_id,
        level=level,
        start_date=start_date,
        end_date=end_date,
        device=device,
    )

    return LogListResponse(
        logs=[LogResponse(**log.to_dict()) for log in logs],
        total=total,
        limit=limit,
        offset=offset,
    )