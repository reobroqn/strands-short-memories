"""
Data models module for the Personal Finance Assistant API.

This module contains Pydantic models for request/response validation
and data serialization across the API.

Exports:
    Request Models:
        - ChatRequest: Request model for chat endpoint
        - MemoryStoreRequest: Request for storing memories
        - MemoryRetrieveRequest: Request for retrieving memories
        - InitializePreferencesRequest: Request for initializing user preferences

    Response Models:
        - ChatResponse: Response from chat endpoint
        - MemoryStoreResponse: Response from memory storage
        - MemoryRetrieveResponse: Response from memory retrieval
        - MemoryListResponse: Response listing all memories
        - AgentStateResponse: Response with agent state information
        - ConversationHistoryResponse: Response with conversation history
        - HealthResponse: Health check response
        - ErrorResponse: Error response model

    Data Models:
        - Memory: Model representing a single memory item
        - MemoryAction: Enum for memory actions (store, retrieve, list)
"""

from .schemas import (
    # Enums
    MemoryAction,

    # Request Models
    ChatRequest,
    MemoryStoreRequest,
    MemoryRetrieveRequest,
    InitializePreferencesRequest,

    # Response Models
    ChatResponse,
    MemoryStoreResponse,
    MemoryRetrieveResponse,
    MemoryListResponse,
    AgentStateResponse,
    ConversationHistoryResponse,
    HealthResponse,
    ErrorResponse,

    # Data Models
    Memory
)

__all__ = [
    # Enums
    "MemoryAction",

    # Request Models
    "ChatRequest",
    "MemoryStoreRequest",
    "MemoryRetrieveRequest",
    "InitializePreferencesRequest",

    # Response Models
    "ChatResponse",
    "MemoryStoreResponse",
    "MemoryRetrieveResponse",
    "MemoryListResponse",
    "AgentStateResponse",
    "ConversationHistoryResponse",
    "HealthResponse",
    "ErrorResponse",

    # Data Models
    "Memory"
]
