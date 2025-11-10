"""
Main FastAPI application for the Personal Finance Assistant.

This application demonstrates the concepts from Lab 2: Memory Integration
of the Strands Agents samples, including:
- Short-term memory: Conversation history, agent state, request state
- Long-term memory: mem0.io integration for persistent user preferences
- Personal finance assistance with context awareness

The application provides a RESTful API for:
- Chat interactions with memory-enabled agents
- Memory management (store, retrieve, list)
- Agent state management
- User preference initialization

Following the tutorial at:
https://github.com/strands-agents/samples/blob/main/02-samples/11-personal-finance-assistant/lab2-memory-integration.ipynb
"""

from contextlib import asynccontextmanager
import logging
import time

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from .api import router
from .config.settings import get_settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(), logging.FileHandler("app.log")],
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for application startup and shutdown.

    Handles:
    - Startup: Initialize resources, log application start
    - Shutdown: Cleanup resources, log application shutdown
    """

    yield


# Initialize FastAPI application
settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    description="""
    ## Tutorial Concepts Demonstrated

    This application implements concepts from the tutorial:

    1. **Conversation History**: Using `SlidingWindowConversationManager` to maintain
       recent messages and manage context length

    2. **Agent State**: Key-value storage for user preferences accessible by tools

    3. **Request State**: Per-request context maintained throughout the event loop

    4. **Long-term Memory**: Integration with mem0.io for:
       - Storing user preferences persistently
       - Retrieving relevant memories via semantic search
       - Listing all stored memories

    5. **Tool Integration**: Using `mem0_memory` and `use_llm` tools for
       memory operations and natural language generation

    ## Getting Started

    1. **Initialize User Preferences** (optional):
       ```
       POST /preferences/initialize
       ```

    2. **Start Chatting**:
       ```
       POST /chat
       ```

    3. **View Memory**:
       ```
       GET /memory/list/{user_id}
       ```

    ## Architecture

    ```
    User Request
         ↓
    FastAPI Endpoint
         ↓
    AgentService
         ↓
    Strands Agent (with mem0_memory, use_llm tools)
         ↓
    AWS Bedrock (Claude 3.7 Sonnet)
         ↓
    mem0.io (FAISS/OpenSearch/Mem0 Platform)
    ```
    """,
    version=settings.app_version,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)


# Global exception handlers


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    Handle request validation errors.

    Returns a structured error response with validation details.
    """
    logger.error(f"Validation error: {exc.errors()}")

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": "ValidationError",
            "message": "Invalid request parameters",
            "detail": exc.errors(),
            "body": exc.body,
        },
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """
    Handle all uncaught exceptions.

    Logs the error and returns a generic error response.
    """
    logger.error(f"Unhandled exception: {exc!s}", exc_info=True)

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "InternalServerError",
            "message": "An unexpected error occurred",
            "detail": str(exc) if settings.debug else "Please contact support",
        },
    )


# Request logging middleware


@app.middleware("http")
async def log_requests(request: Request, call_next):
    """
    Log all incoming requests and their processing time.
    """

    # Log request
    logger.info(f" {request.method} {request.url.path}")

    # Process request and measure time
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time

    # Log response
    logger.info(
        f" {request.method} {request.url.path} "
        f"[{response.status_code}] {process_time:.3f}s"
    )

    # Add processing time header
    response.headers["X-Process-Time"] = str(process_time)

    return response


# Include API routes
app.include_router(router, prefix="/api/v1")


# Root endpoint


@app.get(
    "/",
    tags=["Root"],
    summary="Root Endpoint",
    description="Get basic API information and links",
)
async def root():
    """
    Root endpoint providing API information.

    Returns:
        Dict with API info and useful links
    """
    return {
        "message": "Personal Finance Assistant API",
        "version": settings.app_version,
        "description": "A FastAPI application demonstrating Strands Agents with memory integration",
        "tutorial": "Lab 2: Memory Integration",
        "tutorial_link": "https://github.com/strands-agents/samples/tree/main/02-samples/11-personal-finance-assistant",
        "documentation": "/docs",
        "health_check": "/api/v1/health",
        "educational_notice": "⚠️ This is for educational purposes only, not financial advice",
        "concepts": {
            "short_term_memory": [
                "Conversation History (SlidingWindowConversationManager)",
                "Agent State (user preferences)",
                "Request State (per-request context)",
            ],
            "long_term_memory": [
                "mem0.io integration",
                "Semantic search",
                "Persistent user preferences",
            ],
            "tools": [
                "mem0_memory (store, retrieve, list)",
                "use_llm (natural language generation)",
            ],
        },
        "endpoints": {
            "chat": "POST /api/v1/chat",
            "store_memory": "POST /api/v1/memory/store",
            "retrieve_memories": "POST /api/v1/memory/retrieve",
            "list_memories": "GET /api/v1/memory/list/{user_id}",
            "agent_state": "GET /api/v1/agent/state/{user_id}",
            "conversation_history": "GET /api/v1/agent/history/{user_id}",
            "initialize_preferences": "POST /api/v1/preferences/initialize",
            "reset_agent": "POST /api/v1/agent/reset/{user_id}",
        },
    }


if __name__ == "__main__":
    import uvicorn

    # Run the application
    # For development: uvicorn.run with reload
    # For production: use gunicorn with uvicorn workers
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level="info",
    )
