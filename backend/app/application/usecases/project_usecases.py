import hashlib
import secrets
from typing import List, Optional
from uuid import UUID, uuid4

from app.domain.entities.project import Project
from app.domain.entities.api_key import ApiKey
from app.infrastructure.database.repositories import ProjectRepository, ApiKeyRepository


class ProjectUseCases:
    def __init__(self, project_repo: ProjectRepository, api_key_repo: ApiKeyRepository):
        self.project_repo = project_repo
        self.api_key_repo = api_key_repo

    async def create_project(self, name: str, description: Optional[str] = None) -> tuple[Project, str]:
        project = Project(id=uuid4(), name=name, description=description)
        created_project = await self.project_repo.create(project)

        api_key = self._generate_api_key(created_project.id)
        await self.api_key_repo.create(api_key)

        return created_project, api_key.raw_key

    async def get_project(self, id: UUID) -> Optional[Project]:
        return await self.project_repo.get_by_id(id)

    async def list_projects(self, limit: int = 100, offset: int = 0) -> List[Project]:
        return await self.project_repo.get_all(limit, offset)

    async def update_project(
        self, id: UUID, name: str, description: Optional[str] = None
    ) -> Optional[Project]:
        project = await self.project_repo.get_by_id(id)
        if not project:
            return None
        project.name = name
        project.description = description
        return await self.project_repo.update(project)

    async def delete_project(self, id: UUID) -> bool:
        return await self.project_repo.delete(id)

    async def regenerate_api_key(self, project_id: UUID) -> Optional[str]:
        await self.api_key_repo.deactivate_all_for_project(project_id)
        api_key = self._generate_api_key(project_id)
        await self.api_key_repo.create(api_key)
        return api_key.raw_key

    async def get_project_api_key(self, project_id: UUID) -> Optional[ApiKey]:
        keys = await self.api_key_repo.get_by_project(project_id)
        active_keys = [k for k in keys if k.is_active]
        if not active_keys:
            return None
        active_keys.sort(key=lambda x: x.created_at, reverse=True)
        return active_keys[0]

    def _generate_api_key(self, project_id: UUID) -> ApiKey:
        raw_key = f"{project_id}:{secrets.token_urlsafe(32)}"
        key_hash = hashlib.sha256(raw_key.encode()).hexdigest()
        return ApiKey(
            id=uuid4(),
            project_id=project_id,
            key_hash=key_hash,
            name="default",
            raw_key=raw_key,
        )