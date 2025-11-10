"""
Chat routes - Agent conversation endpoints.

This module contains endpoints for chatting with different types of agents
including basic, financial, memory, budget, and orchestrator agents.
"""

import logging

from fastapi import APIRouter, Depends, HTTPException, status

from ..config.settings import get_settings
from ..models.schemas import ChatRequest, ChatResponse
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


@router.post(
    "/chat",
    response_model=ChatResponse,
    summary="Chat with Agent",
    description="Send a message to any type of agent",
    tags=["Chat"],
)
async def chat_with_agent(
    request: ChatRequest, service: AgentService = Depends(get_agent_service)
):
    """
    Unified chat endpoint supporting multiple agent types.

    Agent types (AgentType enum):
    - AgentType.BASIC: Simple conversational agent
    - AgentType.FINANCIAL: Finance-focused assistant
    - AgentType.MEMORY: Agent with long-term memory
    - AgentType.BUDGET: Agent with budget analysis tools
    - orchestrator: Multi-agent portfolio coordinator

    Uses AgentType.MEMORY as default agent type.
    """
    try:
        # Use default user_id if not provided
        settings = get_settings()
        user_id = request.user_id or settings.default_user_id
        agent_type = AgentType.MEMORY

        logger.info(f"Chat request - User: {user_id}, Agent: {agent_type}")

        result = service.chat(
            user_id=user_id,
            message=request.message,
            agent_type=agent_type,
            session_id=request.session_id,
        )

        return ChatResponse(**result)

    except Exception as e:
        logger.error(f"Chat error: {e!s}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Chat failed: {e!s}",
        ) from e
