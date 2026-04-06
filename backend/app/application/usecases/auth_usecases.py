from datetime import datetime, timedelta
from typing import Optional

from jose import JWTError, jwt
import bcrypt

from app.config import get_settings
from app.infrastructure.database.repositories import AdminUserRepository

settings = get_settings()


class AuthUseCases:
    def __init__(self, admin_user_repo: AdminUserRepository):
        self.admin_user_repo = admin_user_repo

    async def authenticate(self, username: str, password: str) -> Optional[str]:
        user = await self.admin_user_repo.get_by_username(username)
        if not user:
            return None
        password_bytes = password.encode('utf-8')
        hash_bytes = user.password_hash.encode('utf-8') if isinstance(user.password_hash, str) else user.password_hash
        if not bcrypt.checkpw(password_bytes, hash_bytes):
            return None
        return self._create_token(username)

    def _create_token(self, username: str) -> str:
        expire = datetime.utcnow() + timedelta(minutes=settings.jwt_expire_minutes)
        payload = {"sub": username, "exp": expire}
        return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)

    def verify_token(self, token: str) -> Optional[str]:
        try:
            payload = jwt.decode(
                token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm]
            )
            return payload.get("sub")
        except JWTError:
            return None

    async def create_admin_user(self, username: str, password: str) -> None:
        password_bytes = password.encode('utf-8')
        password_hash = bcrypt.hashpw(password_bytes, bcrypt.gensalt()).decode('utf-8')
        await self.admin_user_repo.create(username, password_hash)