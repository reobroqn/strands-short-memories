"""
Memory Service - Memory operations using mem0.io.

This module contains functionality for memory storage, retrieval,
and management using the mem0.io long-term memory system.
"""

import logging
import os
from typing import Any

from mem0 import Memory

logger = logging.getLogger(__name__)


class MemoryService:
    """Memory operations service using mem0.io."""

    def __init__(self):
        """Initialize memory service."""
        # Configure mem0 to use local embeddings
        try:
            # Set a dummy OpenAI key for mem0 to avoid errors
            os.environ["OPENAI_API_KEY"] = "dummy-key-for-mem0"
            self.memory = Memory()
        except Exception as e:
            logger.error(f"Memory service initialization error: {e!s}")
            self.memory = None

    def store_memory(self, user_id: str, content: str) -> dict[str, Any]:
        """Store information in long-term memory."""
        if not self.memory:
            return {
                "success": False,
                "message": "Memory service not available",
                "result": None,
            }
        try:
            result = self.memory(user_id=user_id, operation="store", content=content)
            return {
                "success": True,
                "message": "Memory stored successfully",
                "result": result,
            }
        except Exception as e:
            logger.error(f"Memory storage error: {e!s}")
            return {
                "success": False,
                "message": f"Memory storage failed: {e!s}",
                "result": None,
            }

    def retrieve_memories(
        self,
        user_id: str,
        query: str,
        min_score: float = 0.3,
        max_results: int = 5,
    ) -> dict[str, Any]:
        """Retrieve memories using semantic search."""
        if not self.memory:
            return {"success": False, "results": []}
        try:
            results = self.memory(
                user_id=user_id, operation="search", query=query, limit=max_results
            )

            # Filter by minimum score if applicable
            memories = results.get("results", [])
            if min_score > 0:
                memories = [mem for mem in memories if mem.get("score", 0) >= min_score]

            return {"success": True, "results": memories}
        except Exception as e:
            logger.error(f"Memory retrieval error: {e!s}")
            return {"success": False, "results": []}

    def list_all_memories(self, user_id: str) -> dict[str, Any]:
        """List all memories for a user."""
        if not self.memory:
            return {"success": False, "results": []}
        try:
            results = self.memory(user_id=user_id, operation="get_all")
            return {"success": True, "results": results.get("results", [])}
        except Exception as e:
            logger.error(f"Memory listing error: {e!s}")
            return {"success": False, "results": []}

    def initialize_user_preferences(
        self, user_id: str, preferences: str
    ) -> dict[str, Any]:
        """Initialize user preferences in memory."""
        if not self.memory:
            return {
                "success": False,
                "message": "Memory service not available",
                "result": None,
            }
        try:
            # Store preferences as a special memory
            preference_content = f"USER PREFERENCES: {preferences}"
            result = self.memory(
                user_id=user_id, operation="store", content=preference_content
            )

            return {
                "success": True,
                "message": "User preferences initialized successfully",
                "result": result,
            }
        except Exception as e:
            logger.error(f"Preference initialization error: {e!s}")
            return {
                "success": False,
                "message": f"Preference initialization failed: {e!s}",
                "result": None,
            }
