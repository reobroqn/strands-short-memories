"""
Memory operation schemas.

This module contains Pydantic models for memory operations
including storage, retrieval, and listing functionality.
"""

from pydantic import BaseModel, Field

from .base_schemas import Memory


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
