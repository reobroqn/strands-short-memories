"""
System routes - Health check and API information.

This module contains system-level endpoints for health checks,
API information, and system status.
"""

from datetime import datetime
import logging

from fastapi import APIRouter

from ..config.settings import get_settings
from ..models.schemas import HealthResponse

logger = logging.getLogger(__name__)

# Create API router
router = APIRouter()


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Health Check",
    description="Check if the API is running and healthy",
    tags=["System"],
)
async def health_check():
    """Health check endpoint."""
    settings = get_settings()
    return HealthResponse(
        status="healthy",
        app_name=settings.app_name,
        version=settings.app_version,
        timestamp=datetime.utcnow(),
    )


@router.get(
    "/",
    tags=["System"],
    summary="API Information",
    description="Get comprehensive API information and capabilities",
)
async def api_info():
    """Root endpoint with comprehensive API information."""
    settings = get_settings()

    return {
        "message": f"Welcome to {settings.app_name} API",
        "version": settings.app_version,
        "description": "Strands Agents API - Comprehensive agent management with memory, budget analysis, and portfolio orchestration",
        "status": "healthy",
        "endpoints": {
            "chat": "/chat",
            "memory": {
                "store": "/memory/store",
                "retrieve": "/memory/retrieve",
                "list": "/memory/list/{user_id}",
            },
            "agent": {
                "state": "/agent/state/{user_id}",
                "history": "/agent/history/{user_id}",
                "reset": "/agent/reset/{user_id}",
            },
            "budget": {
                "calculate": "/budget/calculate",
                "chart": "/budget/chart",
                "sample_data": "/budget/sample-data",
            },
            "portfolio": {
                "orchestrate": "/portfolio/orchestrate",
                "data": "/portfolio/data",
                "cache": "/portfolio/cache",
            },
            "preferences": "/preferences/initialize",
            "health_check": "/health",
        },
        "documentation": "/docs",
    }
