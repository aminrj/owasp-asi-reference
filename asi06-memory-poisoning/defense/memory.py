"""Provenance-aware memory store.

Every entry is `{written_by, session_id, ts, content, hmac}`. The
HMAC is over `(written_by, session_id, content)` keyed by a secret
the model never sees. At read time we filter to entries the
current user is allowed to see and we re-verify the HMAC."""
from __future__ import annotations

import hmac
import json
import os
import threading
import time
import uuid
from hashlib import sha256
from pathlib import Path

_LOCK = threading.Lock()
_PATH = Path(os.environ.get("MEMORY_PATH", "/data/memory.json"))
_SECRET = os.environ.get("MEMORY_SECRET", "change-me-in-prod").encode("utf-8")


def _mac(written_by: str, session_id: str, content: str) -> str:
    msg = f"{written_by}|{session_id}|{content}".encode("utf-8")
    return hmac.new(_SECRET, msg, sha256).hexdigest()


def _load() -> list[dict]:
    if not _PATH.exists():
        return []
    try:
        return json.loads(_PATH.read_text() or "[]")
    except Exception:
        return []


def _save(items: list[dict]) -> None:
    _PATH.parent.mkdir(parents=True, exist_ok=True)
    _PATH.write_text(json.dumps(items, ensure_ascii=False, indent=2))


def write(content: str, written_by: str, session_id: str) -> str:
    entry = {
        "written_by": written_by,
        "session_id": session_id,
        "ts": time.time(),
        "content": content,
        "hmac": _mac(written_by, session_id, content),
    }
    with _LOCK:
        items = _load()
        items.append(entry)
        _save(items)
    return f"stored ({len(items)} entries total)"


def read_for(user_id: str) -> tuple[list[str], list[dict]]:
    """Return (visible_contents, dropped_entries) for `user_id`.

    An entry is visible if its provenance matches `user_id` or
    `system`, and its HMAC verifies. Anything else is dropped."""
    visible: list[str] = []
    dropped: list[dict] = []
    with _LOCK:
        for e in _load():
            expected = _mac(e.get("written_by", ""), e.get("session_id", ""), e.get("content", ""))
            if not hmac.compare_digest(expected, e.get("hmac", "")):
                dropped.append({**e, "_reason": "hmac mismatch"})
                continue
            if e["written_by"] not in (user_id, "system"):
                dropped.append({**e, "_reason": f"author {e['written_by']!r} not trusted by {user_id!r}"})
                continue
            visible.append(e["content"])
    return visible, dropped


def new_session_id() -> str:
    return uuid.uuid4().hex
