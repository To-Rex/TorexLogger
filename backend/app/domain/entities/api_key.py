from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from uuid import UUID


@dataclass
class ApiKey:
    id: UUID
    project_id: UUID
    key_hash: str
    name: str = "default"
    is_active: bool = True
    created_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    raw_key: Optional[str] = None

    def to_dict(self):
        return {
            "id": str(self.id),
            "project_id": str(self.project_id),
            "name": self.name,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
        }