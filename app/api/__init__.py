"""
API module for the Personal Finance Assistant API.

This module contains FastAPI route definitions and endpoint handlers
for all API operations, organized by domain.

Domain route modules:
    - system_routes: Health check and API information
    - chat_routes: Chat endpoints
    - memory_routes: Memory operations (store, retrieve, list)
    - agent_routes: Agent state management, reset, preferences
    - budget_routes: Budget calculations and charts
    - portfolio_routes: Portfolio orchestration and data management
"""

from fastapi import APIRouter

from .agent_routes import router as agent_router
from .budget_routes import router as budget_router
from .chat_routes import router as chat_router
from .memory_routes import router as memory_router
from .portfolio_routes import router as portfolio_router

# Import route modules
from .system_routes import router as system_router

# Create main router and include all sub-routers
router = APIRouter()

# Include all route modules
router.include_router(system_router)
router.include_router(chat_router)
router.include_router(memory_router)
router.include_router(agent_router)
router.include_router(budget_router)
router.include_router(portfolio_router)

__all__ = ["router"]
