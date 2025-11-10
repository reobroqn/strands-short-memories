"""
Agent Service - Comprehensive agent management functionality.

This service provides complete agent capabilities:
- Basic and financial agents
- Memory-enabled agents with persistent storage
- Multi-agent orchestration for portfolio management
- Custom tools for budget analysis and visualization
- Portfolio analysis and coordination
"""

import logging
import io
import base64
from typing import Dict, Any, Optional, List
from datetime import datetime

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pandas as pd
import json

from strands import Agent, tool
from strands.models import BedrockModel
from strands.agent.conversation_manager import SlidingWindowConversationManager
from strands_tools import mem0_memory, use_llm

from ..config.settings import get_settings, MEMORY_SYSTEM_PROMPT, BASIC_SYSTEM_PROMPT
from .utils import (
    get_stock_data,
    get_stock_analysis,
    create_growth_portfolio,
    create_diversified_portfolio,
    calculate_portfolio_performance,
    visualize_portfolio_allocation,
    visualize_performance_comparison,
    validate_portfolio_performance
)

logger = logging.getLogger(__name__)


class AgentService:
    """
    Comprehensive agent service combining all functionality.

    Features:
    - Basic and financial agents
    - Memory integration (short-term and long-term)
    - Custom tools for budget analysis and visualization
    - Multi-agent orchestration for portfolio management
    - Specialist agents as tools
    """

    def __init__(self):
        """Initialize the agent service."""
        self.settings = get_settings()
        self.agents: Dict[str, Agent] = {}
        self._cached_stock_data = {}
        self._cached_visualizations = {}

        # Initialize AWS Bedrock model
        self.bedrock_model = BedrockModel(
            model_id=self.settings.bedrock_model_id,
            temperature=self.settings.model_temperature,
            streaming=self.settings.model_streaming
        )

        logger.info(f"UnifiedAgentService initialized with model: {self.settings.bedrock_model_id}")

    # ============================================================================
    # AGENT LIFECYCLE MANAGEMENT
    # ============================================================================

    def get_or_create_agent(
        self,
        user_id: str,
        agent_type: str = "memory",
        initial_state: Optional[Dict[str, Any]] = None
    ) -> Agent:
        """
        Get existing agent or create new one based on type.

        Args:
            user_id: User identifier
            agent_type: Type of agent ("basic", "financial", "memory", "orchestrator")
            initial_state: Optional initial state

        Returns:
            Configured Agent instance
        """
        agent_key = f"{user_id}_{agent_type}"

        if agent_key in self.agents:
            logger.info(f"Returning existing {agent_type} agent for user: {user_id}")
            return self.agents[agent_key]

        logger.info(f"Creating new {agent_type} agent for user: {user_id}")

        if agent_type == "basic":
            agent = self._create_basic_agent()
        elif agent_type == "financial":
            agent = self._create_financial_agent()
        elif agent_type == "budget":
            agent = self._create_budget_agent()
        elif agent_type == "memory":
            agent = self._create_memory_agent(user_id, initial_state)
        elif agent_type == "orchestrator":
            agent = self._create_portfolio_orchestrator()
        else:
            raise ValueError(f"Unknown agent type: {agent_type}")

        self.agents[agent_key] = agent
        return agent

    def _create_basic_agent(self) -> Agent:
        """Create a basic agent without tools or customization."""
        return Agent(model=self.bedrock_model)

    def _create_financial_agent(self) -> Agent:
        """Create a financial agent with specialized system prompt."""
        system_prompt = """You are a helpful personal finance assistant. You provide general strategies
        to creating budgets, tips on financial discipline to achieve financial milestones and analyze
        financial trends. You do not provide any investment advice.

        Keep responses concise and actionable.
        Always provide 2-3 specific steps the user can take.
        Focus on practical budgeting and spending advice.
        """
        return Agent(model=self.bedrock_model, system_prompt=system_prompt)

    def _create_budget_agent(self) -> Agent:
        """Create budget agent with visualization tools."""
        tools = [
            self._get_calculate_budget_tool(),
            self._get_create_chart_tool(),
            self._get_generate_sample_data_tool()
        ]

        system_prompt = """You are a helpful personal finance assistant. You provide general strategies
        to creating budgets, tips on financial discipline to achieve financial milestones and analyze
        financial trends. You do not provide any investment advice.

        Keep responses concise and actionable.
        Always provide 2-3 specific steps the user can take.
        Focus on practical budgeting and spending advice.

        Your capabilities:
        - Calculate 50/30/20 budgets using calculate_budget tool
        - Create visual charts using create_financial_chart tool
        - Generate sample data using generate_sample_data tool

        Always be concise and use tools when appropriate.
        Provide visual output whenever possible.
        """

        return Agent(model=self.bedrock_model, tools=tools, system_prompt=system_prompt)

    def _create_memory_agent(
        self,
        user_id: str,
        initial_state: Optional[Dict[str, Any]] = None
    ) -> Agent:
        """Create memory-enabled agent with conversation management."""
        # Create conversation manager with sliding window
        conversation_manager = SlidingWindowConversationManager(
            window_size=self.settings.conversation_window_size
        )

        # Define memory tools
        @tool
        def mem0_store_memory(content: str) -> str:
            """Store information in long-term memory."""
            try:
                result = mem0_memory(user_id=user_id, operation="store", content=content)
                return f"✅ Stored: {content[:50]}..."
            except Exception as e:
                return f"❌ Storage failed: {str(e)}"

        @tool
        def mem0_retrieve_memories(query: str, max_results: int = 3) -> str:
            """Retrieve relevant memories using semantic search."""
            try:
                memories = mem0_memory(
                    user_id=user_id,
                    operation="retrieve",
                    query=query,
                    max_results=max_results
                )
                if memories:
                    return f"📚 Relevant memories:\n" + "\n".join([
                        f"• {mem.get('text', mem.get('content', ''))}"
                        for mem in memories[:3]
                    ])
                else:
                    return "📚 No relevant memories found."
            except Exception as e:
                return f"❌ Retrieval failed: {str(e)}"

        @tool
        def mem0_list_memories() -> str:
            """List all stored memories."""
            try:
                memories = mem0_memory(user_id=user_id, operation="list")
                if memories:
                    return f"📝 All memories ({len(memories)}):\n" + "\n".join([
                        f"• {mem.get('text', mem.get('content', ''))}"
                        for mem in memories[:5]
                    ])
                else:
                    return "📝 No memories stored."
            except Exception as e:
                return f"❌ List failed: {str(e)}"

        @tool
        def use_llm_tool(prompt: str) -> str:
            """Use LLM for natural language generation."""
            try:
                return use_llm(prompt=prompt)
            except Exception as e:
                return f"❌ LLM call failed: {str(e)}"

        # Configure agent based on memory settings
        tools = [mem0_store_memory, mem0_retrieve_memories, mem0_list_memories, use_llm_tool]

        if self.settings.enable_memory:
            system_prompt = MEMORY_SYSTEM_PROMPT
        else:
            system_prompt = BASIC_SYSTEM_PROMPT
            tools = []

        return Agent(
            model=self.bedrock_model,
            tools=tools,
            conversation_manager=conversation_manager,
            system_prompt=system_prompt,
            state=initial_state or {}
        )

    # ============================================================================
    # CHAT AND CONVERSATION MANAGEMENT
    # ============================================================================

    def chat(
        self,
        user_id: str,
        message: str,
        agent_type: str = "memory",
        session_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Process chat message using specified agent type.

        Args:
            user_id: User identifier
            message: User message
            agent_type: Type of agent to use
            session_id: Optional session identifier

        Returns:
            Response dictionary with agent response and metadata
        """
        try:
            agent = self.get_or_create_agent(user_id, agent_type)
            result = agent(message)

            return {
                "response": str(result),
                "agent_type": agent_type,
                "user_id": user_id,
                "session_id": session_id,
                "timestamp": datetime.utcnow().isoformat()
            }

        except Exception as e:
            logger.error(f"Chat failed for user {user_id}: {str(e)}")
            raise

    # ============================================================================
    # MEMORY OPERATIONS
    # ============================================================================

    def store_memory(self, user_id: str, content: str) -> Dict[str, Any]:
        """Store information in long-term memory."""
        try:
            result = mem0_memory(user_id=user_id, operation="store", content=content)
            return {
                "success": True,
                "message": "Memory stored successfully",
                "result": result
            }
        except Exception as e:
            logger.error(f"Memory storage failed: {str(e)}")
            return {
                "success": False,
                "message": f"Storage failed: {str(e)}"
            }

    def retrieve_memories(
        self,
        user_id: str,
        query: str,
        min_score: float = 0.5,
        max_results: int = 5
    ) -> List[Dict[str, Any]]:
        """Retrieve relevant memories using semantic search."""
        try:
            memories = mem0_memory(
                user_id=user_id,
                operation="retrieve",
                query=query,
                max_results=max_results
            )
            return memories if memories else []
        except Exception as e:
            logger.error(f"Memory retrieval failed: {str(e)}")
            return []

    def list_all_memories(self, user_id: str) -> List[Dict[str, Any]]:
        """List all stored memories for a user."""
        try:
            memories = mem0_memory(user_id=user_id, operation="list")
            return memories if memories else []
        except Exception as e:
            logger.error(f"Memory listing failed: {str(e)}")
            return []

    def initialize_user_preferences(self, user_id: str, preferences: str) -> Dict[str, Any]:
        """Initialize user preferences in long-term memory."""
        return self.store_memory(user_id, f"User preferences: {preferences}")

    # ============================================================================
    # AGENT STATE MANAGEMENT
    # ============================================================================

    def get_agent_state(self, user_id: str) -> Dict[str, Any]:
        """Get current state of memory-enabled agent."""
        try:
            agent = self.get_or_create_agent(user_id, "memory")
            return {
                "agent_id": f"agent_{user_id}",
                "message_count": len(agent.conversation_manager.messages) if hasattr(agent, 'conversation_manager') else 0,
                "state": agent.state if hasattr(agent, 'state') else {},
                "available_tools": [tool.name for tool in agent.tools] if hasattr(agent, 'tools') else []
            }
        except Exception as e:
            logger.error(f"Failed to get agent state: {str(e)}")
            return {"error": str(e)}

    def get_conversation_history(self, user_id: str) -> List[Dict[str, Any]]:
        """Get conversation history for memory-enabled agent."""
        try:
            agent = self.get_or_create_agent(user_id, "memory")
            if hasattr(agent, 'conversation_manager'):
                return [
                    {
                        "role": msg.role,
                        "content": msg.content,
                        "timestamp": msg.timestamp if hasattr(msg, 'timestamp') else None
                    }
                    for msg in agent.conversation_manager.messages
                ]
            return []
        except Exception as e:
            logger.error(f"Failed to get conversation history: {str(e)}")
            return []

    def reset_agent(self, user_id: str) -> None:
        """Reset agent by clearing conversation history and state."""
        try:
            # Remove from active agents cache
            keys_to_remove = [key for key in self.agents.keys() if key.startswith(f"{user_id}_")]
            for key in keys_to_remove:
                del self.agents[key]

            logger.info(f"Reset all agents for user: {user_id}")
        except Exception as e:
            logger.error(f"Failed to reset agent: {str(e)}")
            raise

    # ============================================================================
    # BUDGET AND FINANCIAL TOOLS (Lab 1 functionality)
    # ============================================================================

    def calculate_50_30_20_budget(self, monthly_income: float) -> Dict[str, Any]:
        """Calculate 50/30/20 budget breakdown."""
        try:
            needs = monthly_income * 0.5
            wants = monthly_income * 0.3
            savings = monthly_income * 0.2

            return {
                "monthly_income": monthly_income,
                "needs": {"amount": needs, "percentage": 50},
                "wants": {"amount": wants, "percentage": 30},
                "savings": {"amount": savings, "percentage": 20},
                "total": monthly_income
            }
        except Exception as e:
            logger.error(f"Budget calculation failed: {str(e)}")
            raise

    def create_chart(self, data: Dict[str, float], title: str) -> Dict[str, Any]:
        """Create a pie chart visualization."""
        try:
            plt.figure(figsize=(8, 6))
            plt.pie(data.values(), labels=data.keys(), autopct='%1.1f%%')
            plt.title(title)

            # Save to base64
            buffer = io.BytesIO()
            plt.savefig(buffer, format='png', bbox_inches='tight')
            buffer.seek(0)
            image_base64 = base64.b64encode(buffer.getvalue()).decode()
            plt.close()

            return {
                "title": title,
                "data": data,
                "image_base64": image_base64,
                "chart_type": "pie"
            }
        except Exception as e:
            logger.error(f"Chart creation failed: {str(e)}")
            raise

    def generate_sample_spending_data(self) -> Dict[str, Any]:
        """Generate sample spending data for testing."""
        try:
            categories = {
                "Housing": 1500,
                "Food": 600,
                "Transportation": 400,
                "Utilities": 200,
                "Entertainment": 300,
                "Healthcare": 200,
                "Personal": 250,
                "Savings": 800
            }

            return {
                "categories": categories,
                "total": sum(categories.values()),
                "month": datetime.now().strftime("%B %Y"),
                "description": "Sample monthly spending data"
            }
        except Exception as e:
            logger.error(f"Sample data generation failed: {str(e)}")
            raise

    # ============================================================================
    # MULTI-AGENT ORCHESTRATION (Lab 3 functionality)
    # ============================================================================

    def _create_portfolio_orchestrator(self) -> Agent:
        """Create portfolio orchestrator with specialist agents as tools."""
        specialist_tools = [
            self._create_stock_data_agent(),
            self._create_growth_strategy_agent(),
            self._create_diversified_strategy_agent(),
            self._create_performance_calculator_agent(),
            self._create_visualization_agent(),
            self._create_validation_agent()
        ]

        system_prompt = """You are a Portfolio Orchestrator coordinating multiple specialist agents.

        Your specialist agents:
        1. stock_data_agent - Fetches market data and analysis
        2. growth_strategy_agent - Creates high-growth portfolios
        3. diversified_strategy_agent - Creates balanced portfolios
        4. performance_calculator_agent - Calculates investment projections
        5. visualization_agent - Creates charts and visual outputs
        6. validation_agent - Tests portfolios against real data

        Workflow:
        1. Use stock_data_agent to get market analysis
        2. Use strategy agents (growth/diversified) to create portfolios
        3. Use performance_calculator_agent to project returns
        4. Use validation_agent to test against historical data
        5. Use visualization_agent to create charts
        6. Provide comprehensive recommendation

        Always validate portfolios and provide risk assessments.
        """

        return Agent(
            model=self.bedrock_model,
            tools=specialist_tools,
            system_prompt=system_prompt
        )

    def orchestrate_portfolio(self, user_request: str) -> Dict[str, Any]:
        """Run portfolio orchestration workflow."""
        try:
            orchestrator = self._create_portfolio_orchestrator()
            result = orchestrator(user_request)

            return {
                "success": True,
                "response": str(result),
                "cached_portfolios": self.get_cached_portfolios(),
                "visualizations_available": len(self.get_cached_visualizations()) > 0
            }
        except Exception as e:
            logger.error(f"Portfolio orchestration failed: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }

    # ============================================================================
    # SPECIALIST AGENT IMPLEMENTATIONS
    # ============================================================================

    def _create_stock_data_agent(self) -> tool:
        """Create Stock Data Agent for fetching and analyzing market data."""
        service = self

        @tool
        def stock_data_agent(query: str) -> str:
            """Stock data specialist - fetches market data and provides analysis"""

            @tool
            def stock_data_fetch(tickers: List[str], start_date: str, end_date: str) -> str:
                """Fetch comprehensive stock data."""
                try:
                    data = get_stock_data(tickers, start_date, end_date)
                    service._cached_stock_data['comprehensive'] = data
                    return f"✅ Fetched comprehensive data for {len(tickers)} stocks"
                except Exception as e:
                    return f"❌ Error: {str(e)}"

            @tool
            def stock_analysis_fetch(tickers: List[str], start_date: str, end_date: str) -> str:
                """Fetch stock analysis summary."""
                try:
                    data = get_stock_analysis(tickers, start_date, end_date)
                    service._cached_stock_data['analysis'] = data
                    return f"✅ Analyzed {len(tickers)} stocks"
                except Exception as e:
                    return f"❌ Error: {str(e)}"

            # Create agent with tools
            agent = Agent(
                model=service.bedrock_model,
                tools=[stock_data_fetch, stock_analysis_fetch],
                system_prompt="""You are a Stock Data Specialist.
                Use stock_data_fetch() for comprehensive data or stock_analysis_fetch() for summaries.
                Always verify data quality and provide insights."""
            )

            return agent(query)

        return stock_data_agent

    def _create_growth_strategy_agent(self) -> tool:
        """Create Growth Strategy Agent for high-growth portfolios."""
        service = self

        @tool
        def growth_strategy_agent(request: str) -> str:
            """Growth strategy specialist - creates high-growth portfolios"""

            @tool
            def create_growth_portfolio_tool(analysis_data: dict) -> str:
                """Create growth-focused portfolio."""
                try:
                    portfolio = create_growth_portfolio(analysis_data)
                    service._cached_stock_data['growth_portfolio'] = portfolio
                    return "✅ Created growth portfolio with high-potential stocks"
                except Exception as e:
                    return f"❌ Error: {str(e)}"

            agent = Agent(
                model=service.bedrock_model,
                tools=[create_growth_portfolio_tool],
                system_prompt="""You are a Growth Strategy Specialist.
                Create high-growth portfolios focusing on:
                - Technology and innovation sectors
                - High growth potential
                - Moderate to high risk tolerance
                Always analyze market conditions first."""
            )

            return agent(request)

        return growth_strategy_agent

    def _create_diversified_strategy_agent(self) -> tool:
        """Create Diversified Strategy Agent for balanced portfolios."""
        service = self

        @tool
        def diversified_strategy_agent(request: str) -> str:
            """Diversified strategy specialist - creates balanced portfolios"""

            @tool
            def create_diversified_portfolio_tool(analysis_data: dict) -> str:
                """Create diversified portfolio."""
                try:
                    portfolio = create_diversified_portfolio(analysis_data)
                    service._cached_stock_data['diversified_portfolio'] = portfolio
                    return "✅ Created diversified portfolio with balanced risk"
                except Exception as e:
                    return f"❌ Error: {str(e)}"

            agent = Agent(
                model=service.bedrock_model,
                tools=[create_diversified_portfolio_tool],
                system_prompt="""You are a Diversified Strategy Specialist.
                Create balanced portfolios focusing on:
                - Sector diversification
                - Risk management
                - Stable returns with moderate growth
                Always consider risk tolerance and time horizon."""
            )

            return agent(request)

        return diversified_strategy_agent

    def _create_performance_calculator_agent(self) -> tool:
        """Create Performance Calculator Agent for investment projections."""
        service = self

        @tool
        def performance_calculator_agent(request: str) -> str:
            """Performance calculator specialist - analyzes investment projections"""

            @tool
            def calculate_performance_tool(portfolio: dict, initial_investment: float) -> str:
                """Calculate portfolio performance projections."""
                try:
                    performance = calculate_portfolio_performance(portfolio, initial_investment)
                    service._cached_stock_data['performance'] = performance
                    return f"✅ Calculated performance projections for ${initial_investment:,.2f}"
                except Exception as e:
                    return f"❌ Error: {str(e)}"

            agent = Agent(
                model=service.bedrock_model,
                tools=[calculate_performance_tool],
                system_prompt="""You are a Performance Calculator Specialist.
                Calculate investment projections including:
                - Expected returns
                - Risk metrics
                - Time horizon projections
                Use realistic assumptions and provide ranges."""
            )

            return agent(request)

        return performance_calculator_agent

    def _create_visualization_agent(self) -> tool:
        """Create Visualization Agent for charts and graphs."""
        service = self

        @tool
        def visualization_agent(request: str) -> str:
            """Visualization specialist - creates charts and visual outputs"""

            @tool
            def create_allocation_chart(portfolio: dict) -> str:
                """Create portfolio allocation chart."""
                try:
                    chart_data = visualize_portfolio_allocation(portfolio)
                    service._cached_visualizations['allocation'] = chart_data
                    return "✅ Created portfolio allocation chart"
                except Exception as e:
                    return f"❌ Error: {str(e)}"

            @tool
            def create_performance_chart(performance_data: dict) -> str:
                """Create performance comparison chart."""
                try:
                    chart_data = visualize_performance_comparison(performance_data)
                    service._cached_visualizations['performance'] = chart_data
                    return "✅ Created performance comparison chart"
                except Exception as e:
                    return f"❌ Error: {str(e)}"

            agent = Agent(
                model=service.bedrock_model,
                tools=[create_allocation_chart, create_performance_chart],
                system_prompt="""You are a Visualization Specialist.
                Create clear, informative charts for:
                - Portfolio allocation
                - Performance comparisons
                - Risk-return analysis
                Always use appropriate chart types and clear labels."""
            )

            return agent(request)

        return visualization_agent

    def _create_validation_agent(self) -> tool:
        """Create Validation Agent for testing portfolios."""
        service = self

        @tool
        def validation_agent(request: str) -> str:
            """Validation specialist - tests portfolios against real data"""

            @tool
            def validate_portfolio(portfolio: dict, historical_data: dict) -> str:
                """Validate portfolio against historical data."""
                try:
                    validation_results = validate_portfolio_performance(portfolio, historical_data)
                    service._cached_stock_data['validation'] = validation_results
                    return "✅ Portfolio validation completed"
                except Exception as e:
                    return f"❌ Error: {str(e)}"

            agent = Agent(
                model=service.bedrock_model,
                tools=[validate_portfolio],
                system_prompt="""You are a Validation Specialist.
                Test portfolios against:
                - Historical performance data
                - Risk metrics
                - Market conditions
                Provide objective validation results and recommendations."""
            )

            return agent(request)

        return validation_agent

    # ============================================================================
    # UTILITY METHODS
    # ============================================================================

    def get_cached_portfolios(self) -> Dict[str, Any]:
        """Get all cached portfolio data."""
        return {
            key: data for key, data in self._cached_stock_data.items()
            if 'portfolio' in key.lower()
        }

    def get_cached_visualizations(self) -> Dict[str, Any]:
        """Get all cached visualization data."""
        return self._cached_visualizations

    def clear_cache(self) -> None:
        """Clear all cached data."""
        self._cached_stock_data.clear()
        self._cached_visualizations.clear()
        logger.info("Cache cleared successfully")

    # ============================================================================
    # CUSTOM TOOL IMPLEMENTATIONS
    # ============================================================================

    def _get_calculate_budget_tool(self) -> tool:
        """Get budget calculation tool."""
        service = self

        @tool
        def calculate_budget(monthly_income: float) -> str:
            """Calculate 50/30/20 budget breakdown (Needs/Wants/Savings)."""
            result = service.calculate_50_30_20_budget(monthly_income)
            return f"""Budget Breakdown for ${monthly_income:,.2f}:

            🏠 Needs (50%): ${result['needs']['amount']:,.2f}
            🎯 Wants (30%): ${result['wants']['amount']:,.2f}
            💰 Savings (20%): ${result['savings']['amount']:,.2f}

            Total: ${result['total']:,.2f}
            """

        return calculate_budget

    def _get_create_chart_tool(self) -> tool:
        """Get chart creation tool."""
        service = self

        @tool
        def create_financial_chart(data: Dict[str, float], title: str) -> str:
            """Create a pie chart visualization of financial data."""
            try:
                chart = service.create_chart(data, title)
                return f"✅ Created chart: {title}. Data: {list(data.keys())}"
            except Exception as e:
                return f"❌ Chart creation failed: {str(e)}"

        return create_financial_chart

    def _get_generate_sample_data_tool(self) -> tool:
        """Get sample data generation tool."""
        service = self

        @tool
        def generate_sample_data() -> str:
            """Generate sample spending data for testing."""
            try:
                data = service.generate_sample_spending_data()
                categories = data['categories']
                return f"""Sample Spending Data - {data['month']}:

                {chr(10).join([f'• {cat}: ${amount:,.2f}' for cat, amount in categories.items()])}

                Total: ${data['total']:,.2f}
                """
            except Exception as e:
                return f"❌ Data generation failed: {str(e)}"

        return generate_sample_data