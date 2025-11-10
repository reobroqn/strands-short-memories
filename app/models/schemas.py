"""
Pydantic models for API request and response schemas.

This module defines the data models used for API communication,
including request validation and response serialization.
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


class MemoryStoreRequest(BaseModel):
    """
    Request model for storing memories.

    Attributes:
        content: The content to store in memory
        user_id: User identifier for memory association
    """

    content: str = Field(
        ...,
        description="Content to store in memory",
        min_length=1,
        max_length=10000,
        example="My monthly budget is $4000. I prefer to save 30% and spend 20% on dining.",
    )
    user_id: str = Field(..., description="User identifier", example="user_123")


class MemoryStoreResponse(BaseModel):
    """
    Response model for memory storage.

    Attributes:
        success: Whether the storage was successful
        message: Status message
        memory_id: Optional ID of the stored memory
    """

    success: bool = Field(..., description="Whether the operation was successful")
    message: str = Field(..., description="Status message")
    memory_id: str | None = Field(None, description="ID of the stored memory")


class MemoryRetrieveRequest(BaseModel):
    """
    Request model for retrieving memories.

    Attributes:
        query: Search query for memory retrieval
        user_id: User identifier
        min_score: Minimum relevance score threshold
        max_results: Maximum number of results to return
    """

    query: str = Field(
        ...,
        description="Search query",
        min_length=1,
        example="What are my savings goals?",
    )
    user_id: str = Field(..., description="User identifier", example="user_123")
    min_score: float = Field(
        0.3, description="Minimum relevance score threshold", ge=0.0, le=1.0
    )
    max_results: int = Field(5, description="Maximum number of results", ge=1, le=20)


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


class MemoryRetrieveResponse(BaseModel):
    """
    Response model for memory retrieval.

    Attributes:
        success: Whether the retrieval was successful
        memories: List of retrieved memories
        count: Number of memories retrieved
    """

    success: bool = Field(..., description="Whether the operation was successful")
    memories: list[Memory] = Field(..., description="List of retrieved memories")
    count: int = Field(..., description="Number of memories retrieved", ge=0)


class MemoryListResponse(BaseModel):
    """
    Response model for listing all user memories.

    Attributes:
        success: Whether the operation was successful
        memories: List of all user memories
        count: Total count of memories
        user_id: User identifier
    """

    success: bool = Field(..., description="Whether the operation was successful")
    memories: list[Memory] = Field(..., description="List of all memories")
    count: int = Field(..., description="Total count of memories", ge=0)
    user_id: str = Field(..., description="User identifier")


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


# ============================================================================
# BUDGET AND FINANCIAL ANALYSIS SCHEMAS
# ============================================================================


class BudgetCalculationRequest(BaseModel):
    """Request model for budget calculation."""

    monthly_income: float = Field(
        ..., description="Monthly income amount", gt=0, example=5000.0
    )


class BudgetCalculationResponse(BaseModel):
    """Response model for budget calculation."""

    monthly_income: float = Field(..., description="Monthly income")
    needs: dict[str, Any] = Field(..., description="50% for needs")
    wants: dict[str, Any] = Field(..., description="30% for wants")
    savings: dict[str, Any] = Field(..., description="20% for savings")
    total: float = Field(..., description="Total income")


class ChartRequest(BaseModel):
    """Request model for creating financial charts."""

    data: dict[str, float] = Field(
        ...,
        description="Data to visualize",
        example={"Category A": 100, "Category B": 200},
    )
    title: str = Field(
        ..., description="Chart title", example="Monthly Spending Breakdown"
    )


class ChartResponse(BaseModel):
    """Response model for chart data."""

    title: str = Field(..., description="Chart title")
    data: dict[str, float] = Field(..., description="Data for visualization")
    chart_type: str = Field(default="pie", description="Recommended chart type")
    labels: list[str] = Field(..., description="Labels for chart data")
    values: list[float] = Field(..., description="Values for chart data")


class SampleDataResponse(BaseModel):
    """Response for sample data generation."""

    categories: dict[str, float] = Field(..., description="Spending by category")
    total: float = Field(..., description="Total monthly spending")
    month: str = Field(..., description="Month and year")
    description: str = Field(..., description="Data description")
