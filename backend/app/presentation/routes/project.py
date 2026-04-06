from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.usecases.project_usecases import ProjectUseCases
from app.domain.entities.project import Project
from app.infrastructure.database.connection import get_db
from app.infrastructure.database.repositories import ProjectRepository, ApiKeyRepository
from app.presentation.routes.auth import verify_token
from app.presentation.schemas.project import (
    ProjectCreate,
    ProjectUpdate,
    ProjectResponse,
    ProjectWithApiKey,
)

router = APIRouter(prefix="/api/projects", tags=["projects"])


async def get_project_usecases(session: AsyncSession = Depends(get_db)) -> ProjectUseCases:
    project_repo = ProjectRepository(session)
    api_key_repo = ApiKeyRepository(session)
    yield ProjectUseCases(project_repo, api_key_repo)


@router.post("", response_model=ProjectWithApiKey, status_code=status.HTTP_201_CREATED)
async def create_project(
    request: ProjectCreate,
    _: str = Depends(verify_token),
    usecases: ProjectUseCases = Depends(get_project_usecases),
):
    existing = await usecases.get_project(UUID(int=0))
    try:
        existing = await usecases.project_repo.get_by_name(request.name)
    except Exception:
        pass

    project, raw_key = await usecases.create_project(request.name, request.description)

    return ProjectWithApiKey(
        id=project.id,
        name=project.name,
        description=project.description,
        api_key=raw_key,
        created_at=project.created_at,
        updated_at=project.updated_at,
    )


@router.get("", response_model=List[ProjectWithApiKey])
async def list_projects(
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    _: str = Depends(verify_token),
    usecases: ProjectUseCases = Depends(get_project_usecases),
):
    projects = await usecases.list_projects(limit, offset)
    result = []
    for project in projects:
        api_key_obj = await usecases.get_project_api_key(project.id)
        result.append(ProjectWithApiKey(
            id=project.id,
            name=project.name,
            description=project.description,
            api_key=api_key_obj.raw_key if api_key_obj and api_key_obj.raw_key else "",
            created_at=project.created_at,
            updated_at=project.updated_at,
        ))
    return result


@router.get("/{project_id}", response_model=ProjectWithApiKey)
async def get_project(
    project_id: UUID,
    _: str = Depends(verify_token),
    usecases: ProjectUseCases = Depends(get_project_usecases),
):
    project = await usecases.get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    api_key_obj = await usecases.get_project_api_key(project_id)

    return ProjectWithApiKey(
        id=project.id,
        name=project.name,
        description=project.description,
        api_key=api_key_obj.raw_key if api_key_obj and api_key_obj.raw_key else "",
        created_at=project.created_at,
        updated_at=project.updated_at,
    )


@router.put("/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: UUID,
    request: ProjectUpdate,
    _: str = Depends(verify_token),
    usecases: ProjectUseCases = Depends(get_project_usecases),
):
    project = await usecases.update_project(project_id, request.name, request.description)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(
    project_id: UUID,
    _: str = Depends(verify_token),
    usecases: ProjectUseCases = Depends(get_project_usecases),
):
    deleted = await usecases.delete_project(project_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Project not found")


@router.post("/{project_id}/regenerate-key", response_model=dict)
async def regenerate_api_key(
    project_id: UUID,
    _: str = Depends(verify_token),
    usecases: ProjectUseCases = Depends(get_project_usecases),
):
    project = await usecases.get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    masked_key = await usecases.regenerate_api_key(project_id)
    return {"api_key": masked_key}