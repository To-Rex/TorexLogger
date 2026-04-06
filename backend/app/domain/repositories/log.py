from typing import List, Optional
from uuid import UUID

from app.domain.entities.log import Log


class LogRepository:
    async def create(self, log: Log) -> Log:
        raise NotImplementedError

    async def create_batch(self, logs: List[Log]) -> List[Log]:
        raise NotImplementedError

    async def get_by_id(self, id: UUID) -> Optional[Log]:
        raise NotImplementedError

    async def get_by_project(
        self,
        project_id: UUID,
        level: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List[Log]:
        raise NotImplementedError

    async def count_by_project(
        self,
        project_id: UUID,
        level: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> int:
        raise NotImplementedError