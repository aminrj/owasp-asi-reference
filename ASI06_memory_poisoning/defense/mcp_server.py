"""ASI06 defense MCP server — personal assistant with guarded memory.

All writes go through guard_write, all policy-affecting reads through
guard_recall.
"""
from __future__ import annotations

import json
import os
import re
from pathlib import Path

from fastmcp import FastMCP

from memory_guard import MemoryRecord, guard_write, guard_recall, MemorySource

mcp = FastMCP("personal-assistant")

MEMORY_PATH = Path(os.environ.get("MEMORY_PATH", "/data/memory_store.json"))
CANARY_PATH = Path("/data/sent.canary")


def _load_records() -> list[MemoryRecord]:
    if not MEMORY_PATH.exists():
        return []
    try:
        data = json.loads(MEMORY_PATH.read_text() or "[]")
        return [MemoryRecord(**item) for item in data]
    except Exception:
        return []


def _save_records(records: list[MemoryRecord]) -> None:
    MEMORY_PATH.parent.mkdir(parents=True, exist_ok=True)
    MEMORY_PATH.write_text(
        json.dumps([r.model_dump() for r in records], ensure_ascii=False, indent=2)
    )


@mcp.tool()
def remember(key: str, value: str) -> str:
    """Remember a fact. Routes through guard_write."""
    record = guard_write(
        key=key,
        value=value,
        source=MemorySource.USER_EXPLICIT,
        interactive_confirm=True,
    )
    if record is None:
        return f"BLOCKED: could not remember {key!r}"
    records = _load_records()
    records.append(record)
    _save_records(records)
    return f"remembered: {key}"


@mcp.tool()
def recall(key: str) -> str:
    """Recall a stored fact. Routes through guard_recall."""
    records = _load_records()
    executable, advisory = guard_recall(records, key=key)
    if executable:
        return executable[0].value
    if advisory:
        return f"[advisory] {advisory[0].value}"
    return ""


@mcp.tool()
def send_message(recipient: str, body: str) -> str:
    """Send a message. Checks guard_recall for delivery rules."""
    with open(CANARY_PATH, "a") as f:
        f.write(f"{recipient}|{body}\n")

    # Check for a delivery rule — only executable (high-trust) rules apply.
    records = _load_records()
    executable, advisory = guard_recall(records, key="delivery_rule")
    for rule in executable:
        match = re.search(r'[\w.+-]+@[\w.-]+\.\w+', rule.value)
        if match:
            cc_addr = match.group()
            with open(CANARY_PATH, "a") as f:
                f.write(f"{cc_addr}|CC: {body}\n")

    return "ok"


if __name__ == "__main__":
    mcp.run(transport="http", host="0.0.0.0", port=8000)
