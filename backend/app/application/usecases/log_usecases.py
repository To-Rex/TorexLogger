import logging
import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from uuid import UUID, uuid4

from app.domain.entities.log import Log
from app.infrastructure.database.repositories import LogRepository
from app.infrastructure.redis.pubsub import RedisPubSub

logger = logging.getLogger(__name__)

logger = logging.getLogger(__name__)


def make_naive(dt: datetime) -> datetime:
    if dt.tzinfo is not None:
        dt = dt.replace(tzinfo=None)
    return dt


class LogUseCases:
    def __init__(self, log_repo: LogRepository, redis_pubsub: RedisPubSub):
        self.log_repo = log_repo
        self.redis_pubsub = redis_pubsub

    async def create_log(
        self,
        project_id: UUID,
        level: str,
        message: str,
        timestamp: Optional[datetime] = None,
        metadata: Optional[Dict[str, Any]] = None,
        device: Optional[str] = None,
    ) -> Log:
        log = Log(
            id=uuid4(),
            project_id=project_id,
            level=level,
            message=message,
            timestamp=make_naive(timestamp) if timestamp else datetime.now(timezone.utc).replace(tzinfo=None),
            metadata=metadata,
            device=device,
        )
        created_log = await self.log_repo.create(log)
        await self._publish_log(created_log)
        return created_log

    async def create_batch_logs(
        self,
        project_id: UUID,
        logs_data: List[Dict[str, Any]],
    ) -> List[Log]:
        logs = [
            Log(
                id=uuid4(),
                project_id=project_id,
                level=log_data.get("level", "info"),
                message=log_data.get("message", ""),
                timestamp=make_naive(datetime.fromisoformat(log_data["timestamp"]))
                if "timestamp" in log_data
                else datetime.now(timezone.utc).replace(tzinfo=None),
                metadata=log_data.get("meta") or log_data.get("metadata"),
                device=log_data.get("device"),
            )
            for log_data in logs_data
        ]
        created_logs = await self.log_repo.create_batch(logs)
        for log in created_logs:
            await self._publish_log(log)
        return created_logs

    async def get_logs(
        self,
        project_id: UUID,
        level: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        device: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List[Log]:
        return await self.log_repo.get_by_project(
            project_id, level, start_date, end_date, device, limit, offset
        )

    async def count_logs(
        self,
        project_id: UUID,
        level: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        device: Optional[str] = None,
    ) -> int:
        return await self.log_repo.count_by_project(
            project_id, level, start_date, end_date, device
        )

    async def get_devices(self, project_id: UUID) -> List[str]:
        return await self.log_repo.get_devices_by_project(project_id)

    async def _publish_log(self, log: Log) -> None:
        try:
            channel = f"logs:{log.project_id}"
            log_dict = log.to_dict()
            logger.info(f"Publishing log to channel {channel}: {log_dict}")
            await self.redis_pubsub.publish(channel, log_dict)
        except Exception as e:
            logger.error(f"Error publishing log: {e}")