"""
Data models module for the Personal Finance Assistant API.

This module contains Pydantic models for request/response validation
and data serialization across the API, organized by domain.

Domain modules:
    - base_schemas: Common models (Health, Error, Memory, MemoryAction)
    - chat_schemas: Chat-related models (ChatRequest, ChatResponse)
    - memory_schemas: Memory operation models (Store, Retrieve, List)
    - agent_schemas: Agent state and history models
    - budget_schemas: Budget and chart models (BudgetCalculation, Chart, SampleData)
    - portfolio_schemas: Portfolio-related models
"""

# Base schemas (common models)
# Agent schemas
from .agent_schemas import (
    AgentStateResponse,
    ConversationHistoryResponse,
    InitializePreferencesRequest,
)
from .base_schemas import (
    ErrorResponse,
    HealthResponse,
    Memory,
    MemoryAction,
)

# Budget schemas
from .budget_schemas import (
    BudgetCalculationRequest,
    BudgetCalculationResponse,
    ChartRequest,
    ChartResponse,
    SampleDataResponse,
)

# Chat schemas
from .chat_schemas import (
    ChatRequest,
    ChatResponse,
)

# Memory schemas
from .memory_schemas import (
    MemoryListResponse,
    MemoryRetrieveRequest,
    MemoryRetrieveResponse,
    MemoryStoreRequest,
    MemoryStoreResponse,
)

# Portfolio schemas
from .portfolio_schemas import (
    PortfolioOrchestrationRequest,
)

__all__ = [
    "AgentStateResponse",
    "BudgetCalculationRequest",
    "BudgetCalculationResponse",
    "ChartRequest",
    "ChartResponse",
    "ChatRequest",
    "ChatResponse",
    "ConversationHistoryResponse",
    "ErrorResponse",
    "HealthResponse",
    "InitializePreferencesRequest",
    "Memory",
    "MemoryAction",
    "MemoryListResponse",
    "MemoryRetrieveRequest",
    "MemoryRetrieveResponse",
    "MemoryStoreRequest",
    "MemoryStoreResponse",
    "PortfolioOrchestrationRequest",
    "SampleDataResponse",
]
