from datetime import datetime
from typing import List, Optional
from uuid import UUID, uuid4

from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.domain.entities.project import Project
from app.domain.entities.api_key import ApiKey
from app.domain.entities.log import Log
from app.infrastructure.database.models import (
    ProjectModel,
    ApiKeyModel,
    LogModel,
    AdminUserModel,
)


class ProjectRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, project: Project) -> Project:
        model = ProjectModel(
            id=project.id,
            name=project.name,
            description=project.description,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        self.session.add(model)
        await self.session.commit()
        await self.session.refresh(model)
        return Project(
            id=model.id,
            name=model.name,
            description=model.description,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    async def get_by_id(self, id: UUID) -> Optional[Project]:
        result = await self.session.execute(
            select(ProjectModel).where(ProjectModel.id == id)
        )
        model = result.scalar_one_or_none()
        if not model:
            return None
        return Project(
            id=model.id,
            name=model.name,
            description=model.description,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    async def get_by_name(self, name: str) -> Optional[Project]:
        result = await self.session.execute(
            select(ProjectModel).where(ProjectModel.name == name)
        )
        model = result.scalar_one_or_none()
        if not model:
            return None
        return Project(
            id=model.id,
            name=model.name,
            description=model.description,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    async def get_all(self, limit: int = 100, offset: int = 0) -> List[Project]:
        result = await self.session.execute(
            select(ProjectModel).order_by(ProjectModel.created_at.desc()).limit(limit).offset(offset)
        )
        models = result.scalars().all()
        return [
            Project(
                id=m.id,
                name=m.name,
                description=m.description,
                created_at=m.created_at,
                updated_at=m.updated_at,
            )
            for m in models
        ]

    async def update(self, project: Project) -> Project:
        result = await self.session.execute(
            select(ProjectModel).where(ProjectModel.id == project.id)
        )
        model = result.scalar_one()
        model.name = project.name
        model.description = project.description
        model.updated_at = datetime.utcnow()
        await self.session.commit()
        await self.session.refresh(model)
        return Project(
            id=model.id,
            name=model.name,
            description=model.description,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    async def delete(self, id: UUID) -> bool:
        result = await self.session.execute(
            select(ProjectModel).where(ProjectModel.id == id)
        )
        model = result.scalar_one_or_none()
        if not model:
            return False
        await self.session.delete(model)
        await self.session.commit()
        return True


class ApiKeyRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, api_key: ApiKey) -> ApiKey:
        model = ApiKeyModel(
            id=api_key.id,
            project_id=api_key.project_id,
            key_hash=api_key.key_hash,
            raw_key=api_key.raw_key,
            name=api_key.name,
            is_active=api_key.is_active,
            created_at=datetime.utcnow(),
            expires_at=api_key.expires_at,
        )
        self.session.add(model)
        await self.session.commit()
        await self.session.refresh(model)
        return ApiKey(
            id=model.id,
            project_id=model.project_id,
            key_hash=model.key_hash,
            raw_key=model.raw_key,
            name=model.name,
            is_active=model.is_active,
            created_at=model.created_at,
            expires_at=model.expires_at,
        )

    async def get_by_key_hash(self, key_hash: str) -> Optional[ApiKey]:
        result = await self.session.execute(
            select(ApiKeyModel)
            .where(ApiKeyModel.key_hash == key_hash, ApiKeyModel.is_active == True)
        )
        model = result.scalar_one_or_none()
        if not model:
            return None
        return ApiKey(
            id=model.id,
            project_id=model.project_id,
            key_hash=model.key_hash,
            raw_key=model.raw_key,
            name=model.name,
            is_active=model.is_active,
            created_at=model.created_at,
            expires_at=model.expires_at,
        )

    async def get_by_raw_key(self, raw_key: str) -> Optional[ApiKey]:
        result = await self.session.execute(
            select(ApiKeyModel)
            .where(ApiKeyModel.raw_key == raw_key, ApiKeyModel.is_active == True)
        )
        model = result.scalar_one_or_none()
        if not model:
            return None
        return ApiKey(
            id=model.id,
            project_id=model.project_id,
            key_hash=model.key_hash,
            raw_key=model.raw_key,
            name=model.name,
            is_active=model.is_active,
            created_at=model.created_at,
            expires_at=model.expires_at,
        )

    async def get_by_project(self, project_id: UUID) -> List[ApiKey]:
        result = await self.session.execute(
            select(ApiKeyModel).where(ApiKeyModel.project_id == project_id)
        )
        models = result.scalars().all()
        return [
            ApiKey(
                id=m.id,
                project_id=m.project_id,
                key_hash=m.key_hash,
                raw_key=m.raw_key,
                name=m.name,
                is_active=m.is_active,
                created_at=m.created_at,
                expires_at=m.expires_at,
            )
            for m in models
        ]

    async def deactivate_all_for_project(self, project_id: UUID) -> None:
        result = await self.session.execute(
            select(ApiKeyModel).where(ApiKeyModel.project_id == project_id)
        )
        models = result.scalars().all()
        for model in models:
            model.is_active = False
        await self.session.commit()


class LogRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, log: Log) -> Log:
        model = LogModel(
            id=log.id,
            project_id=log.project_id,
            level=log.level,
            message=log.message,
            timestamp=log.timestamp,
            metadata=log.metadata,
            device=log.device,
            created_at=datetime.utcnow(),
        )
        self.session.add(model)
        await self.session.commit()
        await self.session.refresh(model)
        return Log(
            id=model.id,
            project_id=model.project_id,
            level=model.level,
            message=model.message,
            timestamp=model.timestamp,
            metadata=model.log_metadata,
            device=model.device,
            created_at=model.created_at,
        )

    async def create_batch(self, logs: List[Log]) -> List[Log]:
        models = [
            LogModel(
                id=log.id,
                project_id=log.project_id,
                level=log.level,
                message=log.message,
                timestamp=log.timestamp,
                metadata=log.metadata,
                device=log.device,
                created_at=datetime.utcnow(),
            )
            for log in logs
        ]
        self.session.add_all(models)
        await self.session.commit()
        return logs

    async def get_by_id(self, id: UUID) -> Optional[Log]:
        result = await self.session.execute(select(LogModel).where(LogModel.id == id))
        model = result.scalar_one_or_none()
        if not model:
            return None
        return Log(
            id=model.id,
            project_id=model.project_id,
            level=model.level,
            message=model.message,
            timestamp=model.timestamp,
            metadata=model.log_metadata,
            device=model.device,
            created_at=model.created_at,
        )

    async def get_by_project(
        self,
        project_id: UUID,
        level: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        device: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List[Log]:
        query = select(LogModel).where(LogModel.project_id == project_id)

        if level:
            query = query.where(LogModel.level == level)
        if start_date:
            query = query.where(LogModel.timestamp >= start_date)
        if end_date:
            query = query.where(LogModel.timestamp <= end_date)
        if device:
            query = query.where(LogModel.device == device)

        query = query.order_by(LogModel.timestamp.desc()).limit(limit).offset(offset)

        result = await self.session.execute(query)
        models = result.scalars().all()
        return [
            Log(
                id=m.id,
                project_id=m.project_id,
                level=m.level,
                message=m.message,
                timestamp=m.timestamp,
                metadata=m.log_metadata,
                device=m.device,
                created_at=m.created_at,
            )
            for m in models
        ]

    async def count_by_project(
        self,
        project_id: UUID,
        level: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        device: Optional[str] = None,
    ) -> int:
        query = select(LogModel).where(LogModel.project_id == project_id)

        if level:
            query = query.where(LogModel.level == level)
        if start_date:
            query = query.where(LogModel.timestamp >= start_date)
        if end_date:
            query = query.where(LogModel.timestamp <= end_date)
        if device:
            query = query.where(LogModel.device == device)

        result = await self.session.execute(query)
        return len(result.scalars().all())

    async def get_devices_by_project(self, project_id: UUID) -> List[str]:
        query = (
            select(LogModel.device)
            .where(LogModel.project_id == project_id)
            .where(LogModel.device.isnot(None))
            .distinct()
        )
        result = await self.session.execute(query)
        return [d for d in result.scalars().all() if d]


class AdminUserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_username(self, username: str) -> Optional[AdminUserModel]:
        result = await self.session.execute(
            select(AdminUserModel).where(AdminUserModel.username == username)
        )
        return result.scalar_one_or_none()

    async def create(self, username: str, password_hash: str) -> AdminUserModel:
        model = AdminUserModel(
            id=uuid4(),
            username=username,
            password_hash=password_hash,
            created_at=datetime.utcnow(),
        )
        self.session.add(model)
        await self.session.commit()
        return model