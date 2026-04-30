"""Thin agent harness used by every ASI category demo.

Design goals:
  - Keep the agent loop visible in ~50 LOC.
  - Pluggable tool registry (the attacks live there).
  - No framework dependency beyond the official `ollama` client.
"""
from .agent import Agent, Tool, ToolCall, ToolResult
from .config import AgentConfig

__all__ = ["Agent", "Tool", "ToolCall", "ToolResult", "AgentConfig"]
