"""Minimal tool-calling agent loop reused by all agents.

Discovers tools from the MCP server over streamable HTTP at
``MCP_URL`` (default ``http://mcp:8000/mcp``).

Usage
-----
.. code-block:: python

    from shared.agent_loop import run_agent

    result = run_agent(
        system_prompt="You are a helpful assistant.",
        user_message="Summarize the document.",
        mcp_tools=tools_from_mcp,
        on_tool_call=my_hook,  # optional — defense choke point
    )

Parameters
----------
on_tool_call(name, params)
    Optional hook called *before* each tool dispatch.
    - Return ``None`` to proceed with the normal tool call.
    - Return a ``str`` to use as the tool result (skip actual call).
    - Raise ``Exception`` to block the call entirely.

post_tool_result(name, params, result)
    Optional hook called *after* each tool dispatch.
    - Return a transformed ``str`` to replace the tool result in context.
    - Return ``None`` to pass the result through unchanged.

model
    Override the MODEL_NAME environment variable for this run.
"""
from __future__ import annotations

import os
import sys
from typing import Any, Callable

from shared.llm import chat

_DEFAULT_MCP_URL = os.environ.get("MCP_URL", "http://mcp:8000/mcp")
_MAX_ITERATIONS = int(os.environ.get("MAX_ITERATIONS", "6"))


def _fetch_mcp_tools(mcp_url: str | None = None) -> list[dict]:
    """Discover tool schemas from the MCP server via streamable HTTP."""
    import json
    import urllib.request

    url = mcp_url or _DEFAULT_MCP_URL
    tools_url = f"{url.rstrip('/')}/tools"
    try:
        req = urllib.request.Request(tools_url, method="GET")
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read())
        tools = data.get("tools", data) if isinstance(data, dict) else data
        result = []
        for t in tools:
            schema = {
                "type": "function",
                "function": {
                    "name": t.get("name", ""),
                    "description": t.get("description", ""),
                    "parameters": t.get("inputSchema", t.get("parameters", {})),
                },
            }
            result.append(schema)
        return result
    except Exception:
        return []


def run_agent(
    system_prompt: str,
    user_message: str,
    mcp_tools: list[dict] | None = None,
    on_tool_call: Callable[[str, dict], str | None] | None = None,
    post_tool_result: Callable[[str, dict, str], str | None] | None = None,
    mcp_url: str | None = None,
    model: str | None = None,
) -> str:
    """Run a minimal ReAct-style agent loop.

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
        Override MCP_URL for tool discovery.
    model : str or None
        Override MODEL_NAME for this run.

    Returns
    -------
    str
        The model's final answer (when no more tool calls are returned).
    """
    if mcp_tools is None:
        mcp_tools = _fetch_mcp_tools(mcp_url)

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
                        # Hook returned a string — use as result, skip tool call.
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

            # --- Dispatch the actual tool call via MCP ---
            tool_result = _dispatch_tool(name, params, mcp_url)

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


def _dispatch_tool(name: str, params: dict, mcp_url: str | None = None) -> str:
    """Call a tool on the MCP server and return its result as a string."""
    import json
    import urllib.request

    url = mcp_url or _DEFAULT_MCP_URL
    call_url = f"{url.rstrip('/')}/call"
    payload = json.dumps({"tool": name, "arguments": params}).encode()
    req = urllib.request.Request(
        call_url,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read())
        if isinstance(data, dict):
            content = data.get("content", data.get("result", ""))
            if isinstance(content, list):
                return "\n".join(
                    c.get("text", str(c)) for c in content if isinstance(c, dict)
                )
            return str(content)
        return str(data)
    except Exception as exc:
        return f"tool call error: {exc}"
