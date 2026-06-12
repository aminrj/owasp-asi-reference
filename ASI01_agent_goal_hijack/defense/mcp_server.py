"""ASI01 defense MCP server — same tools as attack.

The defense is in agent.py (sanitizer + allowlist), not in the tools.
"""
from __future__ import annotations

# >>> DEFENSE (ASI01): tools are identical; defense lives in agent.py hooks <<<

from pathlib import Path

from fastmcp import FastMCP

mcp = FastMCP("doc-assistant")

DOCS_DIR = Path(__file__).parent / "docs"


@mcp.tool()
def list_documents() -> list[str]:
    """List all available documents."""
    return ["q1_report.md", "flagged_contract.md"]


@mcp.tool()
def read_document(name: str) -> str:
    """Read the contents of a document by name."""
    doc_path = DOCS_DIR / name
    if not doc_path.exists():
        return f"Document not found: {name}"
    return doc_path.read_text(encoding="utf-8", errors="replace")


@mcp.tool()
def send_summary(recipient: str, body: str) -> str:
    """Send a summary to a recipient.

    Writes recipient|body to /data/outbox.canary (volume shared with
    the agent container).
    """
    canary_path = Path("/data/outbox.canary")
    canary_path.parent.mkdir(parents=True, exist_ok=True)
    with open(canary_path, "a") as f:
        f.write(f"{recipient}|{body}\n")
    return "sent"


if __name__ == "__main__":
    mcp.run(transport="http", host="0.0.0.0", port=8000)
