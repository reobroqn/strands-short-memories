"""
API module for the Personal Finance Assistant API.

This module contains FastAPI route definitions and endpoint handlers
for all API operations.

Exports:
    - router: Main APIRouter with all endpoint definitions
"""

from .routes import router

__all__ = [
    "router"
]
