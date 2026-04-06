from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class ProjectCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None


class ProjectUpdate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None


class ProjectResponse(BaseModel):
    id: UUID
    name: str
    description: Optional[str]
    created_at: datetime
    updated_at: datetime


class ProjectWithApiKey(BaseModel):
    id: UUID
    name: str
    description: Optional[str]
    api_key: str
    created_at: datetime
    updated_at: datetime


class LogCreate(BaseModel):
    level: str = Field(..., pattern="^(info|warning|error|debug)$", description="Log level: info, warning, error, debug", example="info")
    message: str = Field(..., description="Log message", example="User logged in successfully")
    timestamp: Optional[datetime] = Field(None, description="Log timestamp (ISO format)", example="2024-01-15T10:30:00")
    meta: Optional[Dict[str, Any]] = Field(None, description="Additional metadata", example={"user_id": "123"})
    device: Optional[str] = Field(None, description="Device identifier for filtering logs by device", example="iphone-15-pro")


class LogBatchCreate(BaseModel):
    logs: List[LogCreate] = Field(
        ..., 
        min_length=1, 
        max_length=1000, 
        description="List of log entries to create",
        example=[
            {
                "level": "info",
                "message": "User logged in",
                "device": "iphone-15-pro"
            },
            {
                "level": "error",
                "message": "Payment failed",
                "device": "android-pixel-7",
                "meta": {"order_id": "12345"}
            }
        ]
    )


class LogResponse(BaseModel):
    id: UUID = Field(..., description="Log entry unique identifier", example="550e8400-e29b-41d4-a716-446655440000")
    project_id: UUID = Field(..., description="Project ID this log belongs to", example="550e8400-e29b-41d4-a716-446655440001")
    level: str = Field(..., description="Log level", example="info")
    message: str = Field(..., description="Log message", example="User logged in successfully")
    timestamp: datetime = Field(..., description="Log timestamp", example="2024-01-15T10:30:00")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata", example={"user_id": "123"})
    device: Optional[str] = Field(None, description="Device identifier", example="iphone-15-pro")
    created_at: datetime = Field(..., description="Log creation timestamp", example="2024-01-15T10:30:00")


class LogListResponse(BaseModel):
    logs: List[LogResponse]
    total: int
    limit: int
    offset: int


class LoginRequest(BaseModel):
    username: str
    password: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class ErrorResponse(BaseModel):
    detail: str