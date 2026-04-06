from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.usecases.auth_usecases import AuthUseCases
from app.infrastructure.database.connection import get_db
from app.infrastructure.database.repositories import AdminUserRepository
from app.presentation.schemas.project import LoginRequest, LoginResponse, ErrorResponse

router = APIRouter(prefix="/api/auth", tags=["auth"])
security = HTTPBearer()


async def get_auth_usecases(session: AsyncSession = Depends(get_db)):
    repo = AdminUserRepository(session)
    yield AuthUseCases(repo)


@router.post("/login", response_model=LoginResponse)
async def login(
    request: LoginRequest,
    auth_usecases: AuthUseCases = Depends(get_auth_usecases),
):
    token = await auth_usecases.authenticate(request.username, request.password)
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )
    return LoginResponse(access_token=token)


async def verify_token(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    auth_usecases: AuthUseCases = Depends(get_auth_usecases),
) -> str:
    token = credentials.credentials
    username = auth_usecases.verify_token(token)
    if not username:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )
    return username