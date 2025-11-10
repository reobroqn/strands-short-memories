"""
Agent state and management schemas.

This module contains Pydantic models for agent state management,
conversation history, and preference initialization.
"""

from typing import Any

from pydantic import BaseModel, Field


class AgentStateResponse(BaseModel):
    """
    Response model for agent state.

    Attributes:
        agent_id: Agent identifier
        message_count: Number of messages in conversation
        state: Current agent state dictionary
        available_tools: List of available tool names
    """

    agent_id: str = Field(..., description="Agent identifier")
    message_count: int = Field(
        ..., description="Number of messages in conversation", ge=0
    )
    state: dict[str, Any] = Field(..., description="Current agent state")
    available_tools: list[str] = Field(..., description="List of available tool names")


class InitializePreferencesRequest(BaseModel):
    """
    Request model for initializing user preferences.

    Attributes:
        user_id: User identifier
        preferences: User preferences text
    """

    user_id: str = Field(..., description="User identifier", example="user_123")
    preferences: str = Field(
        ...,
        description="User preferences and financial information",
        example="My name is Charlie. I prefer a 40-30-30 budget split...",
    )


class ConversationHistoryResponse(BaseModel):
    """
    Response model for conversation history.

    Attributes:
        user_id: User identifier
        session_id: Session identifier
        messages: List of messages in conversation
        count: Number of messages
    """

    user_id: str = Field(..., description="User identifier")
    session_id: str | None = Field(None, description="Session identifier")
    messages: list[dict[str, Any]] = Field(
        ..., description="List of conversation messages"
    )
    count: int = Field(..., description="Number of messages", ge=0)
