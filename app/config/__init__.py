"""
Configuration module for the Personal Finance Assistant API.

This module provides application settings, environment variable management,
and system prompts for Strands Agents.

Exports:
    - get_settings: Function to get cached settings instance
    - Settings: Settings class for configuration
    - MEMORY_SYSTEM_PROMPT: System prompt for memory-enabled agents
    - BASIC_SYSTEM_PROMPT: System prompt for basic agents
"""

from .settings import BASIC_SYSTEM_PROMPT, MEMORY_SYSTEM_PROMPT, Settings, get_settings

__all__ = ["BASIC_SYSTEM_PROMPT", "MEMORY_SYSTEM_PROMPT", "Settings", "get_settings"]
