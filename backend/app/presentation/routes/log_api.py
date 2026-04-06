import hashlib
from datetime import datetime
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Header, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.usecases.log_usecases import LogUseCases
from app.domain.entities.log import Log
from app.infrastructure.database.connection import get_db
from app.infrastructure.database.repositories import LogRepository, ApiKeyRepository
from app.infrastructure.redis.pubsub import RedisPubSub, get_redis_pubsub
from app.presentation.schemas.project import LogCreate, LogBatchCreate, LogResponse, LogListResponse

router = APIRouter(prefix="/api/logs", tags=["logs"])


async def get_project_from_api_key(
    x_api_key: str = Header(..., alias="x-api-key"),
    session: AsyncSession = Depends(get_db),
) -> UUID:
    key_hash = hashlib.sha256(x_api_key.encode()).hexdigest()
    api_key_repo = ApiKeyRepository(session)
    api_key = await api_key_repo.get_by_key_hash(key_hash)
    if not api_key:
        api_key = await api_key_repo.get_by_raw_key(x_api_key)
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key",
        )
    if api_key.expires_at and api_key.expires_at < datetime.utcnow():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key expired",
        )
    return api_key.project_id


async def get_log_usecases(
    session: AsyncSession = Depends(get_db),
    redis_pubsub: RedisPubSub = Depends(get_redis_pubsub),
) -> LogUseCases:
    log_repo = LogRepository(session)
    return LogUseCases(log_repo, redis_pubsub)


@router.post("", status_code=status.HTTP_201_CREATED, response_model=LogResponse, summary="Create log", description="Create a single log entry with optional device identifier")
async def create_log(
    request: LogCreate,
    project_id: UUID = Depends(get_project_from_api_key),
    usecases: LogUseCases = Depends(get_log_usecases),
):
    log = await usecases.create_log(
        project_id=project_id,
        level=request.level,
        message=request.message,
        timestamp=request.timestamp,
        metadata=request.meta,
        device=request.device,
    )
    return log


@router.post("/batch", status_code=status.HTTP_201_CREATED, response_model=list, summary="Create batch logs", description="Create multiple log entries at once with optional device identifiers")
async def create_batch_logs(
    request: LogBatchCreate,
    project_id: UUID = Depends(get_project_from_api_key),
    usecases: LogUseCases = Depends(get_log_usecases),
):
    logs = await usecases.create_batch_logs(
        project_id=project_id,
        logs_data=[log.model_dump() for log in request.logs],
    )
    return logs