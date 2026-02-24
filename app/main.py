"""Main FastAPI application for the Message API."""

import logging
from fastapi import FastAPI, HTTPException, status
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from datetime import datetime, timezone

from app.config import settings
from app.models import (
    MessageCreateRequest,
    Message,
    ErrorResponse,
    MetricsResponse,
    HealthResponse
)
from app.storage import MessageStorage
from app.metrics import APIMetrics
from app.validators import validate_message, is_duplicate

# Setup logging
logging.basicConfig(
    level=settings.log_level,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global instances
storage = MessageStorage()
metrics = APIMetrics()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Manage application lifecycle.
    """
    logger.info(f"Starting {settings.app_name} v{settings.app_version}")
    yield
    # Cleanup on shutdown
    metrics.log_summary()
    logger.info("Shutting down application")


# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    description=settings.description,
    version=settings.app_version,
    lifespan=lifespan
)


# ==================== Health & System Endpoints ====================

@app.get(
    "/health",
    response_model=HealthResponse,
    tags=["System"],
    summary="Health check endpoint",
    description="Check if the API is running and healthy"
)
async def health_check():
    """Health check endpoint."""
    metrics.record_request("GET", 200, True)
    return HealthResponse(
        status="healthy",
        timestamp=datetime.now(timezone.utc),
        version=settings.app_version
    )


@app.get(
    "/metrics",
    response_model=MetricsResponse,
    tags=["Metrics"],
    summary="Get API metrics and statistics",
    description="Returns comprehensive metrics about the API usage, including request counts, success rates, and message statistics"
)
async def get_metrics():
    """Get API metrics and statistics."""
    metrics_data = metrics.get_metrics()
    message_count = storage.count()
    
    metrics.record_request("GET", 200, True)
    
    return MetricsResponse(
        total_messages=message_count,
        total_requests=metrics_data["total_requests"],
        successful_requests=metrics_data["successful_requests"],
        failed_requests=metrics_data["failed_requests"],
        requests_by_type=metrics_data["requests_by_type"],
        response_codes=metrics_data["response_codes"],
        creation_attempts=metrics_data["creation_attempts"],
        successful_creations=metrics_data["successful_creations"],
        failed_creations=metrics_data["failed_creations"]
    )


# ==================== Message CRUD Endpoints ====================

@app.post(
    "/messages",
    response_model=Message,
    status_code=status.HTTP_201_CREATED,
    tags=["Messages"],
    summary="Create a new message",
    description="Create a new message with validation. The message must be 5-200 characters and contain at least one alphanumeric character.",
    responses={
        201: {
            "description": "Message created successfully",
            "model": Message
        },
        400: {
            "description": "Validation error",
            "model": ErrorResponse
        }
    }
)
async def create_message(request: MessageCreateRequest):
    """
    Create a new message.
    
    Rules:
    - Message must be 5-200 characters
    - Must contain at least 1 alphanumeric character
    - Must not be a duplicate of an existing message
    """
    # Validate message
    is_valid, error_message = validate_message(request.text)
    if not is_valid:
        metrics.record_creation_attempt(False)
        metrics.record_request("POST", 400, False)
        logger.warning(f"Validation failed: {error_message}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "status": 400,
                "code": "VALIDATION_ERROR",
                "message": error_message,
                "details": None
            }
        )
    
    # Check for duplicates
    existing_texts = storage.get_all_texts()
    if is_duplicate(request.text, existing_texts):
        metrics.record_creation_attempt(False)
        metrics.record_request("POST", 409, False)
        logger.warning(f"Duplicate message detected: {request.text[:30]}...")
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "status": 409,
                "code": "DUPLICATE_MESSAGE",
                "message": "Message already exists",
                "details": None
            }
        )
    
    # Create and store message
    message = storage.create(request.text)
    metrics.record_creation_attempt(True)
    metrics.record_request("POST", 201, True)
    
    logger.info(f"Message created: {message.id}")
    return message


@app.get(
    "/messages",
    response_model=list[Message],
    tags=["Messages"],
    summary="Get all messages",
    description="Retrieve all stored messages"
)
async def get_all_messages():
    """
    Get all stored messages.
    """
    messages = storage.get_all()
    metrics.record_request("GET", 200, True)
    
    logger.info(f"Retrieved {len(messages)} messages")
    return messages


@app.get(
    "/messages/{message_id}",
    response_model=Message,
    tags=["Messages"],
    summary="Get a message by ID",
    description="Retrieve a specific message by its ID",
    responses={
        200: {
            "description": "Message found",
            "model": Message
        },
        404: {
            "description": "Message not found",
            "model": ErrorResponse
        }
    }
)
async def get_message(message_id: str):
    """
    Get a message by ID.
    """
    message = storage.get_by_id(message_id)
    
    if message is None:
        metrics.record_request("GET", 404, False)
        logger.warning(f"Message not found: {message_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "status": 404,
                "code": "MESSAGE_NOT_FOUND",
                "message": f"Message with ID '{message_id}' not found",
                "details": None
            }
        )
    
    metrics.record_request("GET", 200, True)
    return message


@app.delete(
    "/messages/{message_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["Messages"],
    summary="Delete a message by ID",
    description="Delete a specific message by its ID",
    responses={
        204: {
            "description": "Message deleted successfully"
        },
        404: {
            "description": "Message not found",
            "model": ErrorResponse
        }
    }
)
async def delete_message(message_id: str):
    """
    Delete a message by ID.
    """
    if not storage.delete(message_id):
        metrics.record_request("DELETE", 404, False)
        logger.warning(f"Attempted to delete non-existent message: {message_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "status": 404,
                "code": "MESSAGE_NOT_FOUND",
                "message": f"Message with ID '{message_id}' not found",
                "details": None
            }
        )
    
    metrics.record_request("DELETE", 204, True)
    logger.info(f"Message deleted: {message_id}")


@app.delete(
    "/messages",
    tags=["Messages"],
    summary="Delete all messages",
    description="Delete all stored messages (reset)",
    responses={
        200: {
            "description": "All messages deleted successfully"
        }
    }
)
async def delete_all_messages():
    """
    Delete all messages (reset endpoint).
    """
    count = storage.delete_all()
    metrics.record_request("DELETE", 200, True)
    
    logger.info(f"All messages deleted. Count: {count}")
    return {
        "status": 200,
        "message": f"All {count} message(s) have been deleted",
        "deleted_count": count
    }


# ==================== Error Handlers ====================

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """
    Custom HTTP exception handler.
    """
    # Handle both standard and detailed error responses
    if isinstance(exc.detail, dict):
        return JSONResponse(
            status_code=exc.status_code,
            content=exc.detail
        )
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "status": exc.status_code,
            "code": "HTTP_ERROR",
            "message": exc.detail,
            "details": None
        }
    )


@app.get("/", tags=["System"], include_in_schema=False)
async def root():
    """Root endpoint with API information."""
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "description": settings.description,
        "documentation": "/docs",
        "health": "/health",
        "metrics": "/metrics"
    }
