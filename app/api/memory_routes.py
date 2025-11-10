"""
Memory routes - Memory operation endpoints.

This module contains endpoints for storing, retrieving, and listing memories
using the mem0.io long-term memory system.
"""

import logging

from fastapi import APIRouter, Depends, HTTPException, status

from ..models.schemas import (
    Memory,
    MemoryListResponse,
    MemoryRetrieveRequest,
    MemoryRetrieveResponse,
    MemoryStoreRequest,
    MemoryStoreResponse,
)
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
    "/memory/store",
    response_model=MemoryStoreResponse,
    summary="Store Memory",
    description="Store information in long-term memory",
    tags=["Memory"],
)
async def store_memory(
    request: MemoryStoreRequest, service: AgentService = Depends(get_agent_service)
):
    """Store information in long-term memory."""
    try:
        result = service.store_memory(user_id=request.user_id, content=request.content)

        return MemoryStoreResponse(
            success=result["success"],
            message=result["message"],
            memory_id=result.get("result", {}).get("id"),
        )

    except Exception as e:
        logger.error(f"Memory storage error: {e!s}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Memory storage failed: {e!s}",
        ) from e


@router.post(
    "/memory/retrieve",
    response_model=MemoryRetrieveResponse,
    summary="Retrieve Memories",
    description="Retrieve relevant memories using semantic search",
    tags=["Memory"],
)
async def retrieve_memories(
    request: MemoryRetrieveRequest, service: AgentService = Depends(get_agent_service)
):
    """Retrieve memories using semantic search."""
    try:
        memories_data = service.retrieve_memories(
            user_id=request.user_id,
            query=request.query,
            min_score=request.min_score,
            max_results=request.max_results,
        )

        memories = [
            Memory(
                id=mem.get("id"),
                content=mem.get("memory"),
                score=mem.get("score"),
                metadata=mem.get("metadata"),
            )
            for mem in memories_data.get("results", [])
        ]

        return MemoryRetrieveResponse(
            success=memories_data.get("success", False),
            memories=memories,
            count=len(memories),
        )

    except Exception as e:
        logger.error(f"Memory retrieval error: {e!s}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Memory retrieval failed: {e!s}",
        ) from e


@router.get(
    "/memory/list/{user_id}",
    response_model=MemoryListResponse,
    summary="List All Memories",
    description="List all stored memories for a user",
    tags=["Memory"],
)
async def list_memories(
    user_id: str, service: AgentService = Depends(get_agent_service)
):
    """List all memories for a user."""
    try:
        memories_data = service.list_all_memories(user_id=user_id)

        memories = [
            Memory(
                id=mem.get("id"),
                content=mem.get("memory"),
                score=mem.get("score"),
                metadata=mem.get("metadata"),
            )
            for mem in memories_data.get("results", [])
        ]

        return MemoryListResponse(
            success=memories_data.get("success", False),
            memories=memories,
            count=len(memories),
            user_id=user_id,
        )

    except Exception as e:
        logger.error(f"Memory listing error: {e!s}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Memory listing failed: {e!s}",
        ) from e
