"""Data models for the Message API."""

from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class MessageCreateRequest(BaseModel):
    """Request model for creating a message."""
    text: str = Field(..., min_length=1, max_length=200)


class Message(BaseModel):
    """Message data model."""
    id: str
    text: str
    created_at: datetime
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "msg_abc123",
                "text": "This is a sample message",
                "created_at": "2026-02-23T10:30:00"
            }
        }


class ErrorResponse(BaseModel):
    """Error response model."""
    status: int
    code: str
    message: str
    details: Optional[dict] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "status": 400,
                "code": "VALIDATION_ERROR",
                "message": "Message must be at least 5 characters",
                "details": None
            }
        }


class MetricsResponse(BaseModel):
    """Metrics response model."""
    total_messages: int
    total_requests: int
    successful_requests: int
    failed_requests: int
    requests_by_type: dict
    response_codes: dict
    creation_attempts: int
    successful_creations: int
    failed_creations: int
    
    class Config:
        json_schema_extra = {
            "example": {
                "total_messages": 42,
                "total_requests": 150,
                "successful_requests": 140,
                "failed_requests": 10,
                "requests_by_type": {"POST": 50, "GET": 80, "DELETE": 20},
                "response_codes": {"200": 80, "201": 50, "400": 10, "404": 5},
                "creation_attempts": 50,
                "successful_creations": 42,
                "failed_creations": 8
            }
        }


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    timestamp: datetime
    version: str
