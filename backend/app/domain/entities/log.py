from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, Optional
from uuid import UUID


@dataclass
class Log:
    id: UUID
    project_id: UUID
    level: str
    message: str
    timestamp: datetime
    metadata: Optional[Dict[str, Any]] = None
    device: Optional[str] = None
    created_at: datetime = None

    def to_dict(self):
        return {
            "id": str(self.id),
            "project_id": str(self.project_id),
            "level": self.level,
            "message": self.message,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "metadata": self.metadata,
            "device": self.device,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }