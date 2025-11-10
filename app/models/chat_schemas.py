"""
Chat-related schemas.

This module contains Pydantic models for chat functionality
including request and response models.
"""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    """
    Request model for chat endpoint.

    Attributes:
        message: The user's message/query
        user_id: Unique identifier for the user (for memory persistence)
        session_id: Optional session identifier for conversation tracking
    """

    message: str = Field(
        ...,
        description="User's message or query",
        min_length=1,
        max_length=5000,
        example="I want to save $800 per month and focus on reducing dining expenses",
    )
    user_id: str | None = Field(
        None,
        description="Unique user identifier for memory persistence",
        example="user_123",
    )
    session_id: str | None = Field(
        None,
        description="Session identifier for conversation tracking",
        example="session_20250101120000",
    )


class ChatResponse(BaseModel):
    """
    Response model for chat endpoint.

    Attributes:
        response: The agent's response message
        user_id: The user ID used for the request
        session_id: The session ID used for the request
        message_count: Number of messages in conversation history
        timestamp: Response timestamp
        metadata: Additional metadata about the response
    """

    response: str = Field(..., description="Agent's response message")
    user_id: str = Field(..., description="User identifier")
    session_id: str | None = Field(None, description="Session identifier")
    message_count: int = Field(
        ..., description="Number of messages in conversation history", ge=0
    )
    timestamp: datetime = Field(
        default_factory=datetime.utcnow, description="Response timestamp"
    )
    metadata: dict[str, Any] | None = Field(
        None, description="Additional response metadata"
    )
