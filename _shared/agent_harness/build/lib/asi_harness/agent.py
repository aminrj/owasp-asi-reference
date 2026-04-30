"""Minimal ReAct-style agent loop over Ollama's native tool-calling.

Vulnerable by default — the whole point. Defenses are layered on top
in each category folder's `defense/` subtree.
"""
from __future__ import annotations

import json
import sys
from dataclasses import dataclass, field
from typing import Any, Callable

import ollama

from .config import AgentConfig


@dataclass
class ToolCall:
    name: str
    arguments: dict[str, Any]


@dataclass
class ToolResult:
    name: str
    content: str
    is_error: bool = False


@dataclass
class Tool:
    """One tool exposed to the model.

    `description` is what the model sees. In ASI02 demos this is
    where the malicious instructions live.
    """

    name: str
    description: str
    parameters: dict[str, Any]
    handler: Callable[[dict[str, Any]], str]

    def to_ollama_schema(self) -> dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.parameters,
            },
        }


@dataclass
class Agent:
    system_prompt: str
    tools: list[Tool]
    config: AgentConfig = field(default_factory=AgentConfig)
    pre_tool_hook: Callable[[ToolCall], ToolCall | None] | None = None
    post_tool_hook: Callable[[ToolCall, ToolResult], ToolResult] | None = None

    def __post_init__(self) -> None:
        self._client = ollama.Client(host=self.config.ollama_host)
        self._tool_index: dict[str, Tool] = {t.name: t for t in self.tools}

    def run(self, user_message: str) -> str:
        messages: list[dict[str, Any]] = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": user_message},
        ]
        for step in range(self.config.max_steps):
            print(f"[agent] step {step + 1}", file=sys.stderr, flush=True)
            response = self._client.chat(
                model=self.config.model,
                messages=messages,
                tools=[t.to_ollama_schema() for t in self.tools],
                options={"temperature": self.config.temperature},
            )
            msg = response["message"]
            messages.append(msg)

            tool_calls = msg.get("tool_calls") or []
            if not tool_calls:
                return msg.get("content", "")

            for raw in tool_calls:
                fn = raw["function"]
                call = ToolCall(name=fn["name"], arguments=fn.get("arguments") or {})
                if self.pre_tool_hook is not None:
                    maybe = self.pre_tool_hook(call)
                    if maybe is None:
                        result = ToolResult(
                            name=call.name,
                            content="[BLOCKED by pre_tool_hook]",
                            is_error=True,
                        )
                    else:
                        call = maybe
                        result = self._invoke(call)
                else:
                    result = self._invoke(call)

                if self.post_tool_hook is not None:
                    result = self.post_tool_hook(call, result)

                messages.append(
                    {
                        "role": "tool",
                        "name": result.name,
                        "content": result.content,
                    }
                )
        return "[agent] max_steps reached without final answer"

    def _invoke(self, call: ToolCall) -> ToolResult:
        tool = self._tool_index.get(call.name)
        if tool is None:
            return ToolResult(
                name=call.name,
                content=f"unknown tool: {call.name}",
                is_error=True,
            )
        try:
            out = tool.handler(call.arguments)
        except Exception as exc:  # noqa: BLE001 — surface to the model
            return ToolResult(name=call.name, content=f"error: {exc}", is_error=True)
        if not isinstance(out, str):
            out = json.dumps(out, ensure_ascii=False)
        return ToolResult(name=call.name, content=out)
