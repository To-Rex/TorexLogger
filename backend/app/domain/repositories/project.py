from typing import List, Optional
from uuid import UUID

from app.domain.entities.project import Project


class ProjectRepository:
    async def create(self, project: Project) -> Project:
        raise NotImplementedError

    async def get_by_id(self, id: UUID) -> Optional[Project]:
        raise NotImplementedError

    async def get_by_name(self, name: str) -> Optional[Project]:
        raise NotImplementedError

    async def get_all(self, limit: int = 100, offset: int = 0) -> List[Project]:
        raise NotImplementedError

    async def update(self, project: Project) -> Project:
        raise NotImplementedError

    async def delete(self, id: UUID) -> bool:
        raise NotImplementedError