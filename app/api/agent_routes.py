"""
Agent routes - Agent state management and preference endpoints.

This module contains endpoints for managing agent state, conversation history,
agent reset, and user preference initialization.
"""

from datetime import datetime
import logging

from fastapi import APIRouter, Depends, HTTPException, status

from ..models.schemas import (
    AgentStateResponse,
    ConversationHistoryResponse,
    InitializePreferencesRequest,
    MemoryStoreResponse,
)
from ..services.agent_manager import AgentType
from ..services.agent_service import AgentService

logger = logging.getLogger(__name__)

# Create API router
router = APIRouter()

# Global service instance
agent_service = AgentService()


def get_agent_service() -> AgentService:
    """Dependency to get the agent service instance."""
    return agent_service


@router.get(
    "/agent/state/{user_id}",
    response_model=AgentStateResponse,
    summary="Get Agent State",
    description="Get the current state of any agent type",
    tags=["Agent"],
)
async def get_agent_state(
    user_id: str,
    agent_type: AgentType = AgentType.MEMORY,
    service: AgentService = Depends(get_agent_service),
):
    """Get agent state information."""
    try:
        state_data = service.get_agent_state(user_id=user_id)
        return AgentStateResponse(**state_data)

    except Exception as e:
        logger.error(f"Agent state error: {e!s}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get agent state: {e!s}",
        ) from e


@router.get(
    "/agent/history/{user_id}",
    response_model=ConversationHistoryResponse,
    summary="Get Conversation History",
    description="Get the conversation history for a user",
    tags=["Agent"],
)
async def get_conversation_history(
    user_id: str, service: AgentService = Depends(get_agent_service)
):
    """Get conversation history."""
    try:
        messages = service.get_conversation_history(user_id=user_id)

        return ConversationHistoryResponse(
            user_id=user_id, session_id=None, messages=messages, count=len(messages)
        )

    except Exception as e:
        logger.error(f"Conversation history error: {e!s}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get conversation history: {e!s}",
        ) from e


@router.post(
    "/agent/reset/{user_id}",
    summary="Reset Agent",
    description="Reset all agents for a user",
    tags=["Agent"],
)
async def reset_agent(user_id: str, service: AgentService = Depends(get_agent_service)):
    """Reset all agents for a user."""
    try:
        service.reset_agent(user_id=user_id)

        return {
            "success": True,
            "message": f"All agents reset for user {user_id}",
            "timestamp": datetime.utcnow(),
        }

    except Exception as e:
        logger.error(f"Agent reset error: {e!s}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to reset agent: {e!s}",
        ) from e


@router.post(
    "/preferences/initialize",
    response_model=MemoryStoreResponse,
    summary="Initialize Preferences",
    description="Initialize user preferences in memory",
    tags=["Agent"],
)
async def initialize_preferences(
    request: InitializePreferencesRequest,
    service: AgentService = Depends(get_agent_service),
):
    """Initialize user preferences."""
    try:
        result = service.initialize_user_preferences(
            user_id=request.user_id, preferences=request.preferences
        )

        return MemoryStoreResponse(
            success=result["success"],
            message="User preferences initialized successfully",
            memory_id=result.get("result", {}).get("id"),
        )

    except Exception as e:
        logger.error(f"Preferences initialization error: {e!s}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to initialize preferences: {e!s}",
        ) from e
