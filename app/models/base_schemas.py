"""
Base schemas - common models used across the application.

This module contains foundational Pydantic models that are shared
across different domains and API endpoints.
"""

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class MemoryAction(str, Enum):
    """Enum for memory tool actions."""

    STORE = "store"
    RETRIEVE = "retrieve"
    LIST = "list"


class Memory(BaseModel):
    """
    Model representing a single memory.

    Attributes:
        id: Memory identifier
        content: Memory content
        score: Relevance score (for retrieved memories)
        metadata: Additional memory metadata
    """

    id: str | None = Field(None, description="Memory identifier")
    content: str = Field(..., description="Memory content")
    score: float | None = Field(None, description="Relevance score", ge=0.0, le=1.0)
    metadata: dict[str, Any] | None = Field(None, description="Additional metadata")


class HealthResponse(BaseModel):
    """
    Response model for health check endpoint.

    Attributes:
        status: Health status
        app_name: Application name
        version: Application version
        timestamp: Health check timestamp
    """

    status: str = Field(..., description="Health status", example="healthy")
    app_name: str = Field(..., description="Application name")
    version: str = Field(..., description="Application version")
    timestamp: datetime = Field(
        default_factory=datetime.utcnow, description="Health check timestamp"
    )


class ErrorResponse(BaseModel):
    """
    Response model for error responses.

    Attributes:
        error: Error type or code
        message: Error message
        detail: Optional detailed error information
        timestamp: Error timestamp
    """

    error: str = Field(..., description="Error type or code", example="ValidationError")
    message: str = Field(
        ..., description="Error message", example="Invalid request parameters"
    )
    detail: Any | None = Field(None, description="Detailed error information")
    timestamp: datetime = Field(
        default_factory=datetime.utcnow, description="Error timestamp"
    )
