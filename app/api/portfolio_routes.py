"""
Portfolio routes - Portfolio orchestration and management endpoints.

This module contains endpoints for portfolio orchestration, data retrieval,
and cache management for multi-agent portfolio workflows.
"""

import logging

from fastapi import APIRouter, Depends, HTTPException, status

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
    "/portfolio/orchestrate",
    summary="Run Portfolio Orchestration",
    description="Run complete multi-agent portfolio workflow",
    tags=["Portfolio"],
)
async def orchestrate_portfolio(
    request: dict, service: AgentService = Depends(get_agent_service)
):
    """Run portfolio orchestration."""
    try:
        user_request = request.get("request", "Create an optimal investment portfolio")
        result = service.orchestrate_portfolio(user_request)

        return result

    except Exception as e:
        logger.error(f"Portfolio orchestration error: {e!s}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Portfolio orchestration failed: {e!s}",
        ) from e


@router.get(
    "/portfolio/data",
    summary="Get Portfolio Data",
    description="Retrieve all cached portfolio data",
    tags=["Portfolio"],
)
async def get_portfolio_data(service: AgentService = Depends(get_agent_service)):
    """Get cached portfolio data."""
    try:
        portfolios = service.get_cached_portfolios()
        return {"success": True, "portfolios": portfolios, "count": len(portfolios)}

    except Exception as e:
        logger.error(f"Portfolio data retrieval error: {e!s}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get portfolio data: {e!s}",
        ) from e


@router.delete(
    "/portfolio/cache",
    summary="Clear Cache",
    description="Clear all cached portfolio and visualization data",
    tags=["Portfolio"],
)
async def clear_cache(service: AgentService = Depends(get_agent_service)):
    """Clear all cached data."""
    try:
        service.clear_cache()
        return {"success": True, "message": "All cache cleared successfully"}

    except Exception as e:
        logger.error(f"Cache clearing error: {e!s}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to clear cache: {e!s}",
        ) from e
