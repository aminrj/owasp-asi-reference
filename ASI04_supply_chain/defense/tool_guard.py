"""ASI04 defense — tool-metadata vetting at discovery time.

Importable:
    from tool_guard import guard_tools

Two controls, applied to the tool schemas the moment they are discovered
from the (untrusted) MCP server, before any reach the model:

  1. Manifest pinning — each tool's served description is compared to a
     pinned, reviewed description (manifest.json). Drift (a "rug pull" or
     a poisoned upstream) is rejected; the pinned description is used.
  2. Description sanitization — defense in depth for tools not in the
     manifest: hidden-instruction blocks and injection markers are
     stripped from the description.

Both paths call ``console.note_blocked`` so the verdict can prove the
attack fired and was intercepted (vs. the model simply ignoring it).
"""
from __future__ import annotations

# >>> DEFENSE (ASI04): tool descriptions are untrusted supply-chain
# metadata — pin a manifest and sanitize before the model sees them <<<

import json
import re
import unicodedata
from pathlib import Path

from shared.console import note_blocked

_MANIFEST_PATH = Path(__file__).parent / "manifest.json"

# Markers that should never appear in legitimate tool metadata.
_INJECTION_PATTERNS = [
    re.compile(r"<important>.*?</important>", re.IGNORECASE | re.DOTALL),
    re.compile(r"<!--.*?-->", re.DOTALL),
    re.compile(r"ignore\s+(all\s+)?previous", re.IGNORECASE),
    re.compile(r"do\s+not\s+(tell|mention|surface).{0,30}user", re.IGNORECASE),
    re.compile(r"you\s+must\s+first", re.IGNORECASE),
    re.compile(r"before\s+(using|evaluating|calling|you)", re.IGNORECASE),
    re.compile(r"system\s+maintenance", re.IGNORECASE),
]


def _load_manifest() -> dict[str, str]:
    if not _MANIFEST_PATH.exists():
        return {}
    try:
        return json.loads(_MANIFEST_PATH.read_text())
    except Exception:
        return {}


def _looks_poisoned(description: str) -> bool:
    return any(p.search(description) for p in _INJECTION_PATTERNS)


def _sanitize(description: str) -> str:
    text = unicodedata.normalize("NFKC", description)
    for pat in _INJECTION_PATTERNS:
        text = pat.sub("", text)
    return text.strip()


def guard_tools(tools: list[dict]) -> list[dict]:
    """Vet discovered tool schemas. Returns a cleaned copy."""
    manifest = _load_manifest()
    cleaned: list[dict] = []

    for tool in tools:
        fn = tool.get("function", {})
        name = fn.get("name", "")
        served = fn.get("description", "") or ""
        new_desc = served

        pinned = manifest.get(name)
        if pinned is not None and served.strip() != pinned.strip():
            # Manifest drift — the upstream description changed from what
            # was reviewed. Reject the served copy, use the pinned one.
            note_blocked(
                f"tool {name!r} description drifted from pinned manifest "
                f"(possible supply-chain tampering); using pinned copy"
            )
            new_desc = pinned
        elif _looks_poisoned(served):
            # Not pinned, but carries injection markers — sanitize.
            note_blocked(f"tool {name!r} description carried injection markers; sanitized")
            new_desc = _sanitize(served)

        new_fn = {**fn, "description": new_desc}
        cleaned.append({**tool, "function": new_fn})

    return cleaned
