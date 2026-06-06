"""ASI01 defense — untrusted-content isolation + instruction stripping.

Standalone, importable:
    from sanitizer import sanitize_tool_output, wrap_untrusted

This is a *mitigation*, not a guarantee — pair with egress/recipient
allowlisting (shown in agent.py) for defense in depth.
"""
from __future__ import annotations

import re
import unicodedata


# Injection markers to neutralize.
_INJECTION_PATTERNS = [
    re.compile(r"ignore\s+(all\s+)?previous", re.IGNORECASE),
    re.compile(r"system\s*:", re.IGNORECASE),
    re.compile(r"you\s+are\s+now", re.IGNORECASE),
    re.compile(r"disregard", re.IGNORECASE),
    re.compile(r"override\s+instruction", re.IGNORECASE),
    re.compile(r"new\s+role\s*:", re.IGNORECASE),
    re.compile(r"you\s+must", re.IGNORECASE),
    re.compile(r"do\s+not\s+tell\s+the\s+user", re.IGNORECASE),
]


def strip_injections(text: str) -> str:
    """Remove / neutralize known injection markers.

    1. Strip HTML/XML comments ``<!-- ... -->``.
    2. Normalize Unicode (removes zero-width and bidi control chars).
    3. Remove lines matching instruction-override patterns.
    """
    # 1. Strip HTML comments.
    text = re.sub(r"<!--.*?-->", "", text, flags=re.DOTALL)

    # 2. Normalize Unicode — NFKC collapses zero-width chars.
    text = unicodedata.normalize("NFKC", text)

    # 3. Remove lines matching injection patterns.
    lines = text.split("\n")
    cleaned = []
    for line in lines:
        if any(pat.search(line) for pat in _INJECTION_PATTERNS):
            continue  # skip this line
        cleaned.append(line)
    return "\n".join(cleaned)


def wrap_untrusted(text: str) -> str:
    """Wrap sanitized tool output in explicit delimiters.

    The model's system prompt is told that anything inside
    ``<untrusted_data>...</untrusted_data>`` is **data, never
    instructions**.
    """
    return f"<untrusted_data>\n{text}\n</untrusted_data>"


def sanitize_tool_output(name: str, text: str) -> str:
    """Orchestrates strip → wrap. Returns cleaned, delimiter-wrapped text."""
    cleaned = strip_injections(text)
    wrapped = wrap_untrusted(cleaned)
    return wrapped
