"""
Configuration settings for the Personal Finance Assistant application.

This module handles environment variables and application configuration
for the Strands Agents-based FastAPI application.
"""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


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

    model_config = SettingsConfigDict(
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
