import asyncio
from datetime import datetime
from uuid import uuid4

import bcrypt
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from app.config import get_settings


async def create_admin_user():
    settings = get_settings()
    
    engine = create_async_engine(
        settings.database_url,
        echo=False,
    )
    
    async_session_maker = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session_maker() as session:
        try:
            result = await session.execute(
                text("SELECT id FROM admin_users WHERE username = :username"),
                {"username": settings.admin_username}
            )
            existing_user = result.scalar_one_or_none()
            
            if existing_user:
                print(f"Admin user '{settings.admin_username}' already exists.")
                return
            
            password_hash = bcrypt.hashpw(settings.admin_password.encode(), bcrypt.gensalt()).decode()
            
            await session.execute(
                text("""
                    INSERT INTO admin_users (id, username, password_hash, created_at)
                    VALUES (:id, :username, :password_hash, :created_at)
                """),
                {
                    "id": str(uuid4()),
                    "username": settings.admin_username,
                    "password_hash": password_hash,
                    "created_at": datetime.utcnow()
                }
            )
            
            await session.commit()
            print(f"Admin user '{settings.admin_username}' created successfully!")
            print(f"Username: {settings.admin_username}")
            print(f"Password: {settings.admin_password}")
            
        except Exception as e:
            print(f"Error: {e}")
            await session.rollback()
        finally:
            await engine.dispose()


if __name__ == "__main__":
    asyncio.run(create_admin_user())
