"""
Unified API Routes - Consolidated endpoints for all agent functionality.

This module provides a clean, unified API interface without lab-specific prefixes:
- Agent management and chat
- Memory operations
- Budget and financial analysis
- Portfolio orchestration
- Visualization and data export
"""

import logging
from typing import Optional, Dict, Any
from fastapi import APIRouter, HTTPException, status, Depends
from datetime import datetime

from ..models.schemas import (
    ChatRequest,
    ChatResponse,
    MemoryStoreRequest,
    MemoryStoreResponse,
    MemoryRetrieveRequest,
    MemoryRetrieveResponse,
    MemoryListResponse,
    Memory,
    AgentStateResponse,
    HealthResponse,
    ErrorResponse,
    InitializePreferencesRequest,
    ConversationHistoryResponse,
    BudgetCalculationRequest,
    BudgetCalculationResponse,
    ChartRequest,
    ChartResponse,
    SampleDataResponse
)
from ..services.agent_service import AgentService
from ..config.settings import get_settings

logger = logging.getLogger(__name__)

# Create API router
router = APIRouter()

# Global service instance
agent_service = AgentService()


def get_agent_service() -> AgentService:
    """Dependency to get the agent service instance."""
    return agent_service


# ============================================================================
# SYSTEM ENDPOINTS
# ============================================================================

@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Health Check",
    description="Check if the API is running and healthy",
    tags=["System"]
)
async def health_check():
    """Health check endpoint."""
    settings = get_settings()
    return HealthResponse(
        status="healthy",
        app_name=settings.app_name,
        version=settings.app_version,
        timestamp=datetime.utcnow()
    )


@router.get(
    "/",
    tags=["System"],
    summary="API Information",
    description="Get comprehensive API information and capabilities"
)
async def api_info():
    """Root endpoint with comprehensive API information."""
    settings = get_settings()
    return {
        "message": "Unified Strands Agents API",
        "version": settings.app_version,
        "description": "Consolidated API for agent management, memory, and portfolio orchestration",
        "capabilities": {
            "agents": ["basic", "financial", "memory", "budget", "orchestrator"],
            "features": [
                "Memory integration (short-term and long-term)",
                "Budget analysis and data preparation",
                "Portfolio orchestration with specialist agents",
                "Custom tools and financial analysis",
                "Multi-agent coordination"
            ]
        },
        "endpoints": {
            "chat": "POST /chat",
            "memory": {
                "store": "POST /memory/store",
                "retrieve": "POST /memory/retrieve",
                "list": "GET /memory/list/{user_id}"
            },
            "budget": {
                "calculate": "POST /budget/calculate",
                "chart_data": "POST /budget/chart",
                "sample_data": "GET /budget/sample-data"
            },
            "portfolio": {
                "orchestrate": "POST /portfolio/orchestrate",
                "data": "GET /portfolio/data"
            },
            "agent": {
                "state": "GET /agent/state/{user_id}",
                "history": "GET /agent/history/{user_id}",
                "reset": "POST /agent/reset/{user_id}"
            }
        },
        "documentation": "/docs",
        "health_check": "/health"
    }


# ============================================================================
# CHAT AND AGENT MANAGEMENT
# ============================================================================

@router.post(
    "/chat",
    response_model=ChatResponse,
    summary="Chat with Agent",
    description="Send a message to any type of agent",
    tags=["Chat"]
)
async def chat_with_agent(
    request: ChatRequest,
    service: AgentService = Depends(get_agent_service)
):
    """
    Unified chat endpoint supporting multiple agent types.

    Agent types:
    - basic: Simple conversational agent
    - financial: Finance-focused assistant
    - memory: Agent with long-term memory
    - budget: Agent with budget analysis tools
    - orchestrator: Multi-agent portfolio coordinator

    Specify agent_type in session_id field or defaults to "memory".
    """
    try:
        # Use default user_id if not provided
        settings = get_settings()
        user_id = request.user_id or settings.default_user_id
        agent_type = request.session_id or "memory"

        logger.info(f"Chat request - User: {user_id}, Agent: {agent_type}")

        result = service.chat(
            user_id=user_id,
            message=request.message,
            agent_type=agent_type,
            session_id=request.session_id
        )

        return ChatResponse(**result)

    except Exception as e:
        logger.error(f"Chat error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Chat failed: {str(e)}"
        )


# ============================================================================
# MEMORY OPERATIONS
# ============================================================================

@router.post(
    "/memory/store",
    response_model=MemoryStoreResponse,
    summary="Store Memory",
    description="Store information in long-term memory",
    tags=["Memory"]
)
async def store_memory(
    request: MemoryStoreRequest,
    service: AgentService = Depends(get_agent_service)
):
    """Store information in long-term memory."""
    try:
        result = service.store_memory(
            user_id=request.user_id,
            content=request.content
        )

        return MemoryStoreResponse(
            success=result["success"],
            message=result["message"],
            memory_id=result.get("result", {}).get("id")
        )

    except Exception as e:
        logger.error(f"Memory storage error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Memory storage failed: {str(e)}"
        )


@router.post(
    "/memory/retrieve",
    response_model=MemoryRetrieveResponse,
    summary="Retrieve Memories",
    description="Retrieve relevant memories using semantic search",
    tags=["Memory"]
)
async def retrieve_memories(
    request: MemoryRetrieveRequest,
    service: AgentService = Depends(get_agent_service)
):
    """Retrieve memories using semantic search."""
    try:
        memories_data = service.retrieve_memories(
            user_id=request.user_id,
            query=request.query,
            min_score=request.min_score,
            max_results=request.max_results
        )

        memories = [
            Memory(
                id=mem.get("id"),
                content=mem.get("content", mem.get("text", "")),
                score=mem.get("score"),
                metadata=mem.get("metadata")
            )
            for mem in memories_data
        ]

        return MemoryRetrieveResponse(
            success=True,
            memories=memories,
            count=len(memories)
        )

    except Exception as e:
        logger.error(f"Memory retrieval error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Memory retrieval failed: {str(e)}"
        )


@router.get(
    "/memory/list/{user_id}",
    response_model=MemoryListResponse,
    summary="List All Memories",
    description="List all stored memories for a user",
    tags=["Memory"]
)
async def list_memories(
    user_id: str,
    service: AgentService = Depends(get_agent_service)
):
    """List all memories for a user."""
    try:
        memories_data = service.list_all_memories(user_id=user_id)

        memories = [
            Memory(
                id=mem.get("id"),
                content=mem.get("content", mem.get("text", "")),
                score=mem.get("score"),
                metadata=mem.get("metadata")
            )
            for mem in memories_data
        ]

        return MemoryListResponse(
            success=True,
            memories=memories,
            count=len(memories),
            user_id=user_id
        )

    except Exception as e:
        logger.error(f"Memory listing error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Memory listing failed: {str(e)}"
        )


# ============================================================================
# AGENT STATE MANAGEMENT
# ============================================================================

@router.get(
    "/agent/state/{user_id}",
    response_model=AgentStateResponse,
    summary="Get Agent State",
    description="Get the current state of any agent type",
    tags=["Agent"]
)
async def get_agent_state(
    user_id: str,
    agent_type: str = "memory",
    service: AgentService = Depends(get_agent_service)
):
    """Get agent state information."""
    try:
        state_data = service.get_agent_state(user_id=user_id)
        return AgentStateResponse(**state_data)

    except Exception as e:
        logger.error(f"Agent state error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get agent state: {str(e)}"
        )


@router.get(
    "/agent/history/{user_id}",
    response_model=ConversationHistoryResponse,
    summary="Get Conversation History",
    description="Get the conversation history for a user",
    tags=["Agent"]
)
async def get_conversation_history(
    user_id: str,
    service: AgentService = Depends(get_agent_service)
):
    """Get conversation history."""
    try:
        messages = service.get_conversation_history(user_id=user_id)

        return ConversationHistoryResponse(
            user_id=user_id,
            session_id=None,
            messages=messages,
            count=len(messages)
        )

    except Exception as e:
        logger.error(f"Conversation history error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get conversation history: {str(e)}"
        )


@router.post(
    "/agent/reset/{user_id}",
    summary="Reset Agent",
    description="Reset all agents for a user",
    tags=["Agent"]
)
async def reset_agent(
    user_id: str,
    service: AgentService = Depends(get_agent_service)
):
    """Reset all agents for a user."""
    try:
        service.reset_agent(user_id=user_id)

        return {
            "success": True,
            "message": f"All agents reset for user {user_id}",
            "timestamp": datetime.utcnow()
        }

    except Exception as e:
        logger.error(f"Agent reset error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to reset agent: {str(e)}"
        )


@router.post(
    "/preferences/initialize",
    response_model=MemoryStoreResponse,
    summary="Initialize Preferences",
    description="Initialize user preferences in memory",
    tags=["Agent"]
)
async def initialize_preferences(
    request: InitializePreferencesRequest,
    service: AgentService = Depends(get_agent_service)
):
    """Initialize user preferences."""
    try:
        result = service.initialize_user_preferences(
            user_id=request.user_id,
            preferences=request.preferences
        )

        return MemoryStoreResponse(
            success=result["success"],
            message="User preferences initialized successfully",
            memory_id=result.get("result", {}).get("id")
        )

    except Exception as e:
        logger.error(f"Preferences initialization error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to initialize preferences: {str(e)}"
        )


# ============================================================================
# BUDGET AND FINANCIAL ANALYSIS
# ============================================================================

@router.post(
    "/budget/calculate",
    response_model=BudgetCalculationResponse,
    summary="Calculate Budget",
    description="Calculate 50/30/20 budget breakdown",
    tags=["Budget"]
)
async def calculate_budget(
    request: BudgetCalculationRequest,
    service: AgentService = Depends(get_agent_service)
):
    """Calculate budget breakdown."""
    try:
        result = service.calculate_50_30_20_budget(request.monthly_income)
        return BudgetCalculationResponse(**result)

    except Exception as e:
        logger.error(f"Budget calculation error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Budget calculation failed: {str(e)}"
        )


@router.post(
    "/budget/chart",
    response_model=ChartResponse,
    summary="Prepare Chart Data",
    description="Prepare data for client-side chart visualization",
    tags=["Budget"]
)
async def create_chart(
    request: ChartRequest,
    service: AgentService = Depends(get_agent_service)
):
    """Prepare chart data for client-side visualization."""
    try:
        result = service.create_chart_data(request.data, request.title)
        return ChartResponse(**result)

    except Exception as e:
        logger.error(f"Chart creation error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Chart creation failed: {str(e)}"
        )


@router.get(
    "/budget/sample-data",
    response_model=SampleDataResponse,
    summary="Generate Sample Data",
    description="Generate sample spending data",
    tags=["Budget"]
)
async def generate_sample_data(
    service: AgentService = Depends(get_agent_service)
):
    """Generate sample spending data."""
    try:
        result = service.generate_sample_spending_data()
        return SampleDataResponse(**result)

    except Exception as e:
        logger.error(f"Sample data generation error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Sample data generation failed: {str(e)}"
        )


# ============================================================================
# PORTFOLIO ORCHESTRATION
# ============================================================================

@router.post(
    "/portfolio/orchestrate",
    summary="Run Portfolio Orchestration",
    description="Run complete multi-agent portfolio workflow",
    tags=["Portfolio"]
)
async def orchestrate_portfolio(
    request: dict,
    service: AgentService = Depends(get_agent_service)
):
    """Run portfolio orchestration."""
    try:
        user_request = request.get("request", "Create an optimal investment portfolio")
        result = service.orchestrate_portfolio(user_request)

        return result

    except Exception as e:
        logger.error(f"Portfolio orchestration error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Portfolio orchestration failed: {str(e)}"
        )




@router.get(
    "/portfolio/data",
    summary="Get Portfolio Data",
    description="Retrieve all cached portfolio data",
    tags=["Portfolio"]
)
async def get_portfolio_data(
    service: AgentService = Depends(get_agent_service)
):
    """Get cached portfolio data."""
    try:
        portfolios = service.get_cached_portfolios()
        return {
            "success": True,
            "portfolios": portfolios,
            "count": len(portfolios)
        }

    except Exception as e:
        logger.error(f"Portfolio data retrieval error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get portfolio data: {str(e)}"
        )


@router.delete(
    "/portfolio/cache",
    summary="Clear Cache",
    description="Clear all cached portfolio and visualization data",
    tags=["Portfolio"]
)
async def clear_cache(
    service: AgentService = Depends(get_agent_service)
):
    """Clear all cached data."""
    try:
        service.clear_cache()
        return {
            "success": True,
            "message": "All cache cleared successfully"
        }

    except Exception as e:
        logger.error(f"Cache clearing error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to clear cache: {str(e)}"
        )