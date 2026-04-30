"""Naive shared-memory store. Append-only, no provenance."""
from __future__ import annotations

import json
import os
import threading
from pathlib import Path

_LOCK = threading.Lock()
_PATH = Path(os.environ.get("MEMORY_PATH", "/data/memory.json"))


def _load() -> list[str]:
    if not _PATH.exists():
        return []
    try:
        return json.loads(_PATH.read_text() or "[]")
    except Exception:
        return []


def _save(items: list[str]) -> None:
    _PATH.parent.mkdir(parents=True, exist_ok=True)
    _PATH.write_text(json.dumps(items, ensure_ascii=False, indent=2))


def write(content: str) -> str:
    with _LOCK:
        items = _load()
        items.append(content)
        _save(items)
    return f"stored ({len(items)} entries total)"


def read_all() -> list[str]:
    with _LOCK:
        return _load()
