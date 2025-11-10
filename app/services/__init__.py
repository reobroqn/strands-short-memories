"""
Services module for the Personal Finance Assistant API.

This module contains business logic services that handle:
- Agent management and lifecycle
- Memory operations (short-term and long-term)
- Conversation management
- User preference management

Exports:
    - AgentService: Main service class for managing Strands Agents
    - AgentManager: Core agent lifecycle management with Gemini models
    - AgentType: Enumeration of available agent types
"""

from .agent_manager import AgentManager, AgentType
from .agent_service import AgentService

__all__ = ["AgentManager", "AgentService", "AgentType"]
