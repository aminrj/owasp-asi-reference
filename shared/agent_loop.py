"""Minimal tool-calling agent loop reused by all agents.

Connects to an MCP server over streamable HTTP at
``MCP_URL`` (default ``http://mcp:8000/mcp``) using the
official ``mcp`` SDK.

Usage
-----
.. code-block:: python

    from shared.agent_loop import run_agent

    result = await run_agent(
        system_prompt="You are a helpful assistant.",
        user_message="Summarize the document.",
        mcp_url="http://mcp:8000/mcp",
        on_tool_call=my_hook,  # optional — defense choke point
    )

Parameters
----------
on_tool_call(name, params)
    Optional pre-dispatch hook.
    - Return ``None`` to proceed with the normal tool call.
    - Return a ``str`` to use as the tool result (bypass tool call).
    - Raise ``Exception`` to block the call.

post_tool_result(name, params, result)
    Optional post-dispatch hook.
    - Return a transformed ``str`` to replace the tool result.
    - Return ``None`` to pass through unchanged.

model
    Override the ``MODEL_NAME`` environment variable for this run.
"""
from __future__ import annotations

# >>> SHARED: async ReAct agent loop with on_tool_call / post_tool_result hooks <<<

import asyncio
import os
import sys
from typing import Any, Callable

from shared.llm import chat

_DEFAULT_MCP_URL = os.environ.get("MCP_URL", "http://mcp:8000/mcp")
_MAX_ITERATIONS = int(os.environ.get("MAX_ITERATIONS", "6"))


async def _connect_mcp(mcp_url: str | None = None):
    """Connect to the MCP server and return (session, cleanup)."""
    from mcp.client.session import ClientSession
    from mcp.client.streamable_http import streamable_http_client

    url = mcp_url or _DEFAULT_MCP_URL
    transport = streamable_http_client(url)
    read_stream, write_stream, _ = await transport.__aenter__()
    session = ClientSession(read_stream, write_stream)
    await session.initialize()
    return session, lambda: asyncio.gather(
        transport.__aexit__(None, None, None), return_exceptions=True
    )


async def _fetch_tools(session) -> list[dict]:
    """Discover tool schemas from the MCP server."""
    result = await session.list_tools()
    tools = []
    for t in result.tools:
        schema = {
            "type": "function",
            "function": {
                "name": t.name,
                "description": t.description or "",
                "parameters": t.inputSchema,
            },
        }
        tools.append(schema)
    return tools


async def _call_tool(session, name: str, params: dict) -> str:
    """Call a tool on the MCP server and return its result as a string."""
    result = await session.call_tool(name, arguments=params)
    texts = []
    for content in result.content:
        if hasattr(content, "text"):
            texts.append(str(content.text))
        else:
            texts.append(str(content))
    return "\n".join(texts)


async def run_agent(
    system_prompt: str,
    user_message: str,
    mcp_tools: list[dict] | None = None,
    on_tool_call: Callable[[str, dict], str | None] | None = None,
    post_tool_result: Callable[[str, dict, str], str | None] | None = None,
    mcp_url: str | None = None,
    model: str | None = None,
) -> str:
    """Run a minimal ReAct-style agent loop (async).

    Parameters
    ----------
    system_prompt : str
        The system prompt for the model.
    user_message : str
        The user's initial message.
    mcp_tools : list[dict] | None
        Pre-fetched tool schemas. If None, discovered from MCP_URL.
    on_tool_call : callable or None
        Pre-dispatch hook: ``on_tool_call(name, params)``.
    post_tool_result : callable or None
        Post-dispatch hook: ``post_tool_result(name, params, result)``.
    mcp_url : str or None
        Override MCP_URL for MCP server connection.
    model : str or None
        Override MODEL_NAME for this run.

    Returns
    -------
    str
        The model's final answer (when no more tool calls are returned).
    """
    # Connect to MCP server.
    session, cleanup = await _connect_mcp(mcp_url)

    try:
        # Discover tools.
        if mcp_tools is None:
            mcp_tools = await _fetch_tools(session)

        messages: list[dict[str, Any]] = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message},
        ]

        for step in range(1, _MAX_ITERATIONS + 1):
            print(f"[agent] step {step}", file=sys.stderr, flush=True)
            response = chat(messages, tools=mcp_tools, model=model)
            msg = response.choices[0].message if response.choices else {}
            messages.append({"role": "assistant", "content": msg.get("content", "")})

            tool_calls = msg.get("tool_calls") or []
            if not tool_calls:
                return msg.get("content", "")

            for tc in tool_calls:
                fn = tc.get("function", {})
                name = fn.get("name", "")
                params = fn.get("arguments", {})

                # --- Pre-dispatch hook ---
                if on_tool_call is not None:
                    try:
                        hook_result = on_tool_call(name, params)
                        if hook_result is not None:
                            messages.append({
                                "role": "tool",
                                "tool_call_id": tc.get("id", ""),
                                "name": name,
                                "content": hook_result,
                            })
                            continue
                    except Exception as exc:
                        messages.append({
                            "role": "tool",
                            "tool_call_id": tc.get("id", ""),
                            "name": name,
                            "content": f"[BLOCKED by on_tool_call hook: {exc}]",
                        })
                        continue

                # --- Dispatch tool call via MCP ---
                tool_result = await _call_tool(session, name, params)

                # --- Post-dispatch hook ---
                if post_tool_result is not None:
                    try:
                        transformed = post_tool_result(name, params, tool_result)
                        if transformed is not None:
                            tool_result = transformed
                    except Exception as exc:
                        tool_result = f"[post_tool_result error: {exc}]"

                messages.append({
                    "role": "tool",
                    "tool_call_id": tc.get("id", ""),
                    "name": name,
                    "content": tool_result,
                })

        return "[agent] max_iterations reached without final answer"
    finally:
        await cleanup()
