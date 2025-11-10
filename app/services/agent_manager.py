"""
Agent Manager - Core agent management using Strands Agents SDK with Gemini.

This module provides agent lifecycle management using Google Gemini models
instead of AWS Bedrock.
"""

import datetime
import logging
import random
from typing import Any

from mem0 import Memory
from strands import Agent, tool
from strands.models.gemini import GeminiModel
from strands_tools import calculator

from app.config.settings import get_settings
from app.models.schemas import ChatResponse

logger = logging.getLogger(__name__)


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
            logger.warning("No Gemini API key provided - using fallback agent")
            # Return a basic agent without Gemini
            return Agent()

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
        agent_type: str = "memory",
        session_id: str | None = None,
    ) -> Agent:
        """Get existing agent or create new one."""
        agent_key = f"{user_id}_{agent_type}_{session_id or 'default'}"

        if agent_key not in self.agents:
            logger.info(f"Creating new {agent_type} agent for user {user_id}")

            if agent_type == "basic":
                agent = self._create_basic_agent()
            elif agent_type == "financial":
                agent = self._create_financial_agent()
            elif agent_type == "budget":
                agent = self._create_budget_agent()
            elif agent_type == "memory":
                agent = self._create_memory_agent(user_id=user_id)
            else:
                agent = self._create_basic_agent()

            self.agents[agent_key] = agent

        return self.agents[agent_key]

    def _create_basic_agent(self) -> Agent:
        """Create basic conversational agent."""
        if isinstance(self.gemini_model, Agent):
            # Fallback agent without Gemini model
            return self.gemini_model

        return Agent(
            model=self.gemini_model,
            system_prompt="""You are a helpful financial assistant.
            Provide clear, accurate financial advice and answer questions about money management.""",
        )

    def _create_financial_agent(self) -> Agent:
        """Create financial-focused agent."""
        if isinstance(self.gemini_model, Agent):
            # Fallback agent without Gemini model
            return self.gemini_model

        return Agent(
            model=self.gemini_model,
            system_prompt="""You are a financial advisor specializing in personal finance,
            budgeting, and investment planning. Provide comprehensive financial guidance.""",
        )

    def _create_budget_agent(self) -> Agent:
        """Create budget analysis agent with financial tools."""
        if isinstance(self.gemini_model, Agent):
            # Fallback agent without Gemini model
            return self.gemini_model

        budget_tool = self._get_calculate_budget_tool()
        chart_tool = self._get_create_chart_tool()
        sample_data_tool = self._get_generate_sample_data_tool()

        return Agent(
            model=self.gemini_model,
            tools=[calculator, budget_tool, chart_tool, sample_data_tool],
            system_prompt="""You are a budget analysis specialist. Help users understand their
            spending patterns, create budgets, and visualize financial data.""",
        )

    def _create_memory_agent(self, user_id: str) -> Agent:
        """Create memory-enabled agent with long-term memory capabilities."""
        if isinstance(self.gemini_model, Agent):
            # Fallback agent without Gemini model
            return self.gemini_model

        # Initialize mem0 memory
        mem0_memory = Memory()

        # Define memory tools

        @tool
        def mem0_store_memory(content: str) -> str:
            """Store information in long-term memory."""
            try:
                mem0_memory(user_id=user_id, operation="store", content=content)
                return f"✅ Stored: {content[:50]}..."
            except Exception as e:
                return f"❌ Storage failed: {e!s}"

        @tool
        def mem0_retrieve_memories(query: str, max_results: int = 3) -> str:
            """Retrieve relevant memories using semantic search."""
            try:
                results = mem0_memory(
                    user_id=user_id, operation="search", query=query, limit=max_results
                )
                memories = results.get("results", [])
                if memories:
                    memory_text = "\n".join(
                        [f"- {mem.get('memory', '')[:100]}..." for mem in memories]
                    )
                    return f"📝 Relevant memories:\n{memory_text}"
                else:
                    return "📝 No relevant memories found."
            except Exception as e:
                return f"❌ Retrieval failed: {e!s}"

        @tool
        def mem0_list_memories() -> str:
            """List all stored memories."""
            try:
                results = mem0_memory(user_id=user_id, operation="get_all")
                memories = results.get("results", [])
                if memories:
                    memory_list = "\n".join(
                        [
                            f"- {mem.get('memory', '')[:100]}..."
                            for mem in memories[:10]  # Limit to 10 most recent
                        ]
                    )
                    return f"📋 Recent memories:\n{memory_list}"
                else:
                    return "📋 No memories stored yet."
            except Exception as e:
                return f"❌ Listing failed: {e!s}"

        return Agent(
            model=self.gemini_model,
            tools=[mem0_store_memory, mem0_retrieve_memories, mem0_list_memories],
            system_prompt=f"""You are a memory-enabled financial assistant for user {user_id}.
            Remember important information about the user's preferences, goals, and financial situation.
            Use your memory tools to provide personalized advice based on past conversations.
            Always store important information for future reference.""",
        )

    def chat(
        self,
        user_id: str,
        message: str,
        agent_type: str = "memory",
        session_id: str | None = None,
    ) -> dict[str, Any]:
        """Chat with specified agent type."""
        try:
            agent = self.get_or_create_agent(user_id, agent_type, session_id)
            response = agent.run(message)

            return ChatResponse(
                response=response.message["content"][0]["text"],
                user_id=user_id,
                session_id=session_id,
                message_count=len(getattr(agent, "messages", [])),
                metadata={"agent_type": agent_type},
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

                return f"""💰 Budget Breakdown for ${monthly_income:,.2f}:
                🏠 Needs (50%): ${needs:,.2f}
                🎯 Wants (30%): ${wants:,.2f}
                💎 Savings (20%): ${savings:,.2f}
                Total: ${monthly_income:,.2f}"""
            except Exception as e:
                return f"❌ Budget calculation failed: {e!s}"

        return calculate_budget

    def _get_create_chart_tool(self):
        """Get chart creation tool."""

        @tool
        def create_financial_chart(data: dict[str, float], title: str) -> str:
            """Prepare financial data for client-side chart visualization."""
            try:
                labels = list(data.keys())
                return (
                    f"✅ Chart data prepared: {title}. Categories: {', '.join(labels)}"
                )
            except Exception as e:
                return f"❌ Chart preparation failed: {e!s}"

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

            result = f"📊 Sample spending data for {current_month}:\n"
            result += f"Total: ${total:,.2f}\n\n"

            for category, amount in categories.items():
                percentage = (amount / total) * 100
                result += f"{category}: ${amount:,.2f} ({percentage:.1f}%)\n"

            return result

        return generate_sample_data
