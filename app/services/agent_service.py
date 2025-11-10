"""
Unified Agent Service - Consolidated agent management for all functionality.

This module provides a single entry point for all agent operations using
Strands Agents SDK with Google Gemini models.
"""

import datetime
import logging
import random
from typing import Any

from .agent_manager import AgentManager
from .memory_service import MemoryService

logger = logging.getLogger(__name__)


class AgentService:
    """
    Main service class for managing Strands Agents with Gemini models.

    This service acts as a unified interface for:
    - Agent lifecycle management
    - Memory operations using mem0.io
    - Budget and financial analysis
    - Portfolio orchestration
    """

    def __init__(self):
        """Initialize the agent service with all components."""
        self.agent_manager = AgentManager()
        self.memory_service = MemoryService()
        self._cached_stock_data = {}
        self._cached_portfolios = {}

    # Chat and Agent Management
    def chat(
        self,
        user_id: str,
        message: str,
        agent_type: str = "memory",
        session_id: str | None = None,
    ) -> dict[str, Any]:
        """Chat with specified agent type."""
        return self.agent_manager.chat(user_id, message, agent_type, session_id)

    def get_agent_state(self, user_id: str) -> dict[str, Any]:
        """Get agent state information."""
        try:
            agent = self.agent_manager.get_or_create_agent(user_id, "memory")
            messages = getattr(agent, "messages", [])

            return {
                "agent_id": f"{user_id}_memory",
                "message_count": len(messages),
                "state": {"status": "active", "model": "gemini"},
                "available_tools": agent.tool_names
                if hasattr(agent, "tool_names")
                else [],
            }
        except Exception as e:
            logger.error(f"Failed to get agent state: {e!s}")
            raise

    def get_conversation_history(self, user_id: str) -> list[dict[str, Any]]:
        """Get conversation history."""
        try:
            agent = self.agent_manager.get_or_create_agent(user_id, "memory")
            messages = getattr(agent, "messages", [])

            return [
                {
                    "role": msg.get("role", "unknown"),
                    "content": msg.get("content", ""),
                    "timestamp": msg.get("timestamp", ""),
                }
                for msg in messages
            ]
        except Exception as e:
            logger.error(f"Failed to get conversation history: {e!s}")
            raise

    def reset_agent(self, user_id: str) -> None:
        """Reset agent by clearing conversation history and state."""
        try:
            # Remove from active agents cache
            keys_to_remove = [
                key
                for key in self.agent_manager.agents
                if key.startswith(f"{user_id}_")
            ]
            for key in keys_to_remove:
                del self.agent_manager.agents[key]

            logger.info(f"Reset all agents for user: {user_id}")
        except Exception as e:
            logger.error(f"Failed to reset agent: {e!s}")
            raise

    # Memory Operations
    def store_memory(self, user_id: str, content: str) -> dict[str, Any]:
        """Store information in long-term memory."""
        return self.memory_service.store_memory(user_id, content)

    def retrieve_memories(
        self,
        user_id: str,
        query: str,
        min_score: float = 0.3,
        max_results: int = 5,
    ) -> dict[str, Any]:
        """Retrieve memories using semantic search."""
        return self.memory_service.retrieve_memories(
            user_id, query, min_score, max_results
        )

    def list_all_memories(self, user_id: str) -> list[dict[str, Any]]:
        """List all memories for a user."""
        result = self.memory_service.list_all_memories(user_id)
        return result.get("results", [])

    def initialize_user_preferences(
        self, user_id: str, preferences: str
    ) -> dict[str, Any]:
        """Initialize user preferences in memory."""
        return self.memory_service.initialize_user_preferences(user_id, preferences)

    # Budget and Financial Analysis
    def calculate_50_30_20_budget(self, monthly_income: float) -> dict[str, Any]:
        """Calculate 50/30/20 budget breakdown."""
        needs = monthly_income * 0.50
        wants = monthly_income * 0.30
        savings = monthly_income * 0.20

        return {
            "monthly_income": monthly_income,
            "needs": {"amount": needs, "percentage": 50},
            "wants": {"amount": wants, "percentage": 30},
            "savings": {"amount": savings, "percentage": 20},
            "total": monthly_income,
        }

    def create_chart_data(self, data: dict[str, float], title: str) -> dict[str, Any]:
        """Create chart data for client-side visualization."""
        return {
            "title": title,
            "data": data,
            "chart_type": "pie",
            "labels": list(data.keys()),
            "values": list(data.values()),
        }

    def generate_sample_spending_data(self) -> dict[str, Any]:
        """Generate sample spending data."""
        categories = {
            "Housing": random.uniform(1200, 2000),
            "Food": random.uniform(400, 800),
            "Transportation": random.uniform(200, 600),
            "Entertainment": random.uniform(100, 400),
            "Utilities": random.uniform(150, 300),
            "Healthcare": random.uniform(100, 500),
            "Personal": random.uniform(100, 300),
            "Savings": random.uniform(200, 1000),
        }

        current_month = datetime.datetime.now().strftime("%B %Y")
        total = sum(categories.values())

        return {
            "categories": categories,
            "total": round(total, 2),
            "month": current_month,
            "description": f"Sample spending data for {current_month}",
        }

    # Portfolio Operations
    def orchestrate_portfolio(self, user_request: str) -> dict[str, Any]:
        """Run portfolio orchestration workflow."""
        try:
            # For now, return a simple response
            # In a full implementation, this would use the portfolio orchestration agent
            return {
                "success": True,
                "message": "Portfolio orchestration completed",
                "request": user_request,
                "result": {
                    "strategy": "diversified",
                    "allocation": {
                        "Stocks": 60.0,
                        "Bonds": 30.0,
                        "Cash": 10.0,
                    },
                    "expected_return": 8.5,
                    "risk_level": "Moderate",
                },
            }
        except Exception as e:
            logger.error(f"Portfolio orchestration error: {e!s}")
            raise

    def get_cached_portfolios(self) -> dict[str, Any]:
        """Retrieve all cached portfolio data."""
        return self._cached_portfolios

    def clear_cache(self) -> None:
        """Clear all cached data."""
        self._cached_stock_data.clear()
        self._cached_portfolios.clear()
        logger.info("All cache cleared successfully")
