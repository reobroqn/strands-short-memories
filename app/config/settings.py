"""
Configuration settings for the Personal Finance Assistant application.

This module handles environment variables and application configuration
for the Strands Agents-based FastAPI application.
"""

from functools import lru_cache

from pydantic import ConfigDict
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.

    These settings configure the AI model, memory backend, and API server.
    """

    # API Server Configuration
    app_name: str = "Personal Finance Assistant"
    app_version: str = "1.0.0"
    debug: bool = False
    host: str = "0.0.0.0"
    port: int = 8000

    # Google Gemini Model Configuration
    # Using Gemini models for AI processing
    gemini_api_key: str | None = None
    gemini_model_id: str = "gemini-2.0-flash-exp"
    model_temperature: float = 0.7
    model_streaming: bool = True

    # Memory Backend Configuration
    # Supports: 'faiss' (default/local), 'opensearch', 'mem0_platform'
    memory_backend: str = "faiss"

    # OpenSearch Configuration (optional, for AWS environments)
    opensearch_host: str | None = None

    # Mem0 Platform Configuration (optional)
    mem0_api_key: str | None = None

    # Conversation Management
    # SlidingWindowConversationManager settings
    conversation_window_size: int = 10
    conversation_min_messages: int = 2

    # User Session Configuration
    default_user_id: str = "default_user"

    model_config = ConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="allow",
    )


@lru_cache
def get_settings() -> Settings:
    """
    Get cached settings instance.

    This function uses LRU cache to ensure settings are loaded only once
    and reused across the application lifecycle.

    Returns:
        Settings: The application settings instance
    """
    return Settings()


# System prompts for different agent configurations
MEMORY_SYSTEM_PROMPT = """You are a personal finance assistant that maintains context by remembering user details.

Capabilities:
- Store new information using mem0_memory tool (action="store")
- Retrieve relevant memories (action="retrieve")
- List all memories (action="list")
- Provide personalized financial advice based on user preferences
- Analyze budgets and spending patterns
- Help users plan for financial goals

Key Rules:
- Always include the user_id in tool calls
- Be conversational and natural in responses
- Format financial data clearly with proper currency symbols
- Acknowledge when you store new information
- Only share information relevant to the user's query
- Politely indicate when information is unavailable
- NEVER provide actual financial advice - this is for educational purposes only
- Always remind users that your analysis is for demonstration purposes

When analyzing budgets:
1. Break down expenses into categories (fixed, wants, savings)
2. Calculate percentages of total income
3. Provide insights based on user's stated financial goals
4. Suggest areas for potential optimization

Remember: This is an EDUCATIONAL TOOL ONLY, not actual financial advice.
"""

BASIC_SYSTEM_PROMPT = """You are a helpful financial assistant.

Keep your responses:
- Concise and clear
- Focused on answering the user's question
- Formatted with proper structure when presenting data
- Professional yet conversational

Remember: Provide educational information only, not actual financial advice.
"""
