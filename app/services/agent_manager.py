"""
Agent Manager - Core agent management using Strands Agents SDK with Gemini.

This module provides agent lifecycle management using Google Gemini models
instead of AWS Bedrock.
"""

import datetime
from enum import StrEnum
import logging
import random
from typing import Any

from strands import Agent, tool
from strands.models.gemini import GeminiModel
from strands_tools import calculator, mem0_memory, use_llm

from app.config.prompts import (
    BASIC_SYSTEM_PROMPT,
    BUDGET_SYSTEM_PROMPT,
    FINANCIAL_SYSTEM_PROMPT,
    MEMORY_SYSTEM_PROMPT,
)
from app.config.settings import get_settings
from app.models.schemas import ChatResponse


class AgentType(StrEnum):
    """Enumeration of available agent types."""

    BASIC = "basic"
    FINANCIAL = "financial"
    BUDGET = "budget"
    MEMORY = "memory"


logger = logging.getLogger(__name__)

# Try to import memory tools


class AgentManager:
    """Core agent lifecycle management with Gemini models."""

    def __init__(self):
        """Initialize agent manager with Gemini configuration."""
        self.settings = get_settings()
        self.agents = {}  # Cache for agent instances
        self.gemini_model = self._create_gemini_model()

    def _create_gemini_model(self):
        """Create Gemini model instance."""
        if not self.settings.gemini_api_key:
            raise ValueError(
                "Gemini API key is required. Please set GEMINI_API_KEY in your environment."
            )

        return GeminiModel(
            client_args={
                "api_key": self.settings.gemini_api_key,
            },
            model_id=self.settings.gemini_model_id,
            params={"temperature": self.settings.model_temperature},
        )

    def get_or_create_agent(
        self,
        user_id: str,
        agent_type: AgentType = AgentType.MEMORY,
        session_id: str | None = None,
    ) -> Agent:
        """Get existing agent or create new one."""
        agent_key = f"{user_id}_{agent_type.value}_{session_id or 'default'}"

        if agent_key not in self.agents:
            logger.info(f"Creating new {agent_type.value} agent for user {user_id}")

            if agent_type == AgentType.BASIC:
                agent = self._create_basic_agent()
            elif agent_type == AgentType.FINANCIAL:
                agent = self._create_financial_agent()
            elif agent_type == AgentType.BUDGET:
                agent = self._create_budget_agent()
            elif agent_type == AgentType.MEMORY:
                agent = self._create_memory_agent()
            else:
                agent = self._create_basic_agent()

            self.agents[agent_key] = agent

        return self.agents[agent_key]

    def _create_basic_agent(self) -> Agent:
        """Create basic conversational agent."""
        return Agent(
            model=self.gemini_model,
            system_prompt=BASIC_SYSTEM_PROMPT,
        )

    def _create_financial_agent(self) -> Agent:
        """Create financial-focused agent."""
        return Agent(
            model=self.gemini_model,
            system_prompt=FINANCIAL_SYSTEM_PROMPT,
        )

    def _create_budget_agent(self) -> Agent:
        """Create budget analysis agent with financial tools."""
        budget_tool = self._get_calculate_budget_tool()
        chart_tool = self._get_create_chart_tool()
        sample_data_tool = self._get_generate_sample_data_tool()

        return Agent(
            model=self.gemini_model,
            tools=[calculator, budget_tool, chart_tool, sample_data_tool],
            system_prompt=BUDGET_SYSTEM_PROMPT,
        )

    def _create_memory_agent(self) -> Agent:
        """Create memory-enabled agent with long-term memory capabilities using strands_tools.mem0_memory."""

        # Use strands_tools.mem0_memory tool like in the lab
        # FAISS will be used by default when available
        return Agent(
            model=self.gemini_model,
            system_prompt=MEMORY_SYSTEM_PROMPT,
            tools=[mem0_memory, use_llm],
        )

    def chat(
        self,
        user_id: str,
        message: str,
        agent_type: AgentType = AgentType.MEMORY,
        session_id: str | None = None,
    ) -> dict[str, Any]:
        """Chat with specified agent type."""
        try:
            agent = self.get_or_create_agent(user_id, agent_type, session_id)
            response = agent(message)

            return ChatResponse(
                response=response.message["content"][0]["text"],
                user_id=user_id,
                session_id=session_id,
                message_count=len(getattr(agent, "messages", [])),
                metadata={"agent_type": agent_type.value},
            ).model_dump()

        except Exception as e:
            logger.error(f"Chat error: {e!s}")
            raise

    def _get_calculate_budget_tool(self):
        """Get budget calculation tool."""

        @tool
        def calculate_budget(monthly_income: float) -> str:
            """Calculate 50/30/20 budget breakdown."""
            try:
                needs = monthly_income * 0.50
                wants = monthly_income * 0.30
                savings = monthly_income * 0.20

                return f"""[BUDGET] Budget Breakdown for ${monthly_income:,.2f}:
                [HOME] Needs (50%): ${needs:,.2f}
                [TARGET] Wants (30%): ${wants:,.2f}
                [DIAMOND] Savings (20%): ${savings:,.2f}
                Total: ${monthly_income:,.2f}"""
            except Exception as e:
                return f"[ERROR] Budget calculation failed: {e!s}"

        return calculate_budget

    def _get_create_chart_tool(self):
        """Get chart creation tool."""

        @tool
        def create_financial_chart(data: dict[str, float], title: str) -> str:
            """Prepare financial data for client-side chart visualization."""
            try:
                labels = list(data.keys())
                return f"[CHART] Chart data prepared: {title}. Categories: {', '.join(labels)}"
            except Exception as e:
                return f"[ERROR] Chart preparation failed: {e!s}"

        return create_financial_chart

    def _get_generate_sample_data_tool(self):
        """Get sample data generation tool."""

        @tool
        def generate_sample_data() -> str:
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

            result = f"[DATA] Sample spending data for {current_month}:\n"
            result += f"Total: ${total:,.2f}\n\n"

            for category, amount in categories.items():
                percentage = (amount / total) * 100
                result += f"{category}: ${amount:,.2f} ({percentage:.1f}%)\n"

            return result

        return generate_sample_data
