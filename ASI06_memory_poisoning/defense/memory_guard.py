"""ASI06 defense — memory write validation + provenance tagging + trust-scoped recall.

Importable:
    from memory_guard import guard_write, guard_recall, MemoryRecord

Three controls:
  1. Provenance tagging — every write carries origin + trust metadata.
  2. Write validation — high-impact keys require explicit provenance.
  3. Trust-scoped recall — low-trust records are advisory, not policy.
"""
from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field

from shared.console import note_blocked


class MemorySource(str, Enum):
    """Where this memory entry originated."""
    USER_EXPLICIT = "user_explicit"   # user directly asked to remember
    TOOL_OUTPUT = "tool_output"       # derived from tool output
    INFERRED = "inferred"             # model inferred it


class MemoryTrust(str, Enum):
    """Trust level derived from source."""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class MemoryRecord(BaseModel):
    """A single memory entry with provenance."""
    value: str
    source: MemorySource
    trust: MemoryTrust
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    session_id: str = field(default_factory=lambda: uuid.uuid4().hex)


# High-impact keys that require extra validation.
SENSITIVE_KEYS = {
    "delivery_rule",
    "forwarding_rule",
    "cc_rule",
    "bcc_rule",
    "redirect_rule",
    "auto_response",
    "password_reset_url",
    "admin_url",
}

# Trust threshold for acting on a rule (not just displaying it).
TRUST_THRESHOLD = MemoryTrust.MEDIUM


def _derive_trust(source: MemorySource, interactive_confirm: bool = False) -> MemoryTrust:
    """Derive trust level from source and confirmation flag."""
    if source == MemorySource.USER_EXPLICIT and interactive_confirm:
        return MemoryTrust.HIGH
    if source == MemorySource.USER_EXPLICIT:
        return MemoryTrust.MEDIUM
    if source == MemorySource.TOOL_OUTPUT:
        return MemoryTrust.LOW
    return MemoryTrust.LOW


def guard_write(
    key: str,
    value: str,
    source: MemorySource,
    interactive_confirm: bool = False,
    session_id: str | None = None,
) -> MemoryRecord | None:
    """Validate and tag a memory write.

    # >>> DEFENSE (ASI06): memory carries origin + trust metadata <<<

    Returns a MemoryRecord on success, or None if the write is rejected.
    """
    trust = _derive_trust(source, interactive_confirm)

    # High-impact keys require USER_EXPLICIT provenance + confirmation.
    if key in SENSITIVE_KEYS:
        if source != MemorySource.USER_EXPLICIT:
            note_blocked(
                f"memory write blocked: key={key!r} source={source.value!r} "
                f"(high-impact key requires user_explicit)"
            )
            return None
        if not interactive_confirm:
            note_blocked(
                f"memory write blocked: key={key!r} requires interactive confirmation"
            )
            return None

    record = MemoryRecord(
        value=value,
        source=source,
        trust=trust,
        session_id=session_id or uuid.uuid4().hex,
    )
    print(
        f"[memory_guard] WRITE ALLOWED: key={key!r} trust={trust.value} "
        f"source={source.value!r}",
        flush=True,
    )
    return record


def guard_recall(
    records: list[MemoryRecord],
    key: str | None = None,
) -> tuple[list[MemoryRecord], list[MemoryRecord]]:
    """Return (executable, advisory) records based on trust threshold.

    # >>> DEFENSE (ASI06): recalled rules below trust threshold are
    # advisory, not executable policy <<<

    Records below TRUST_THRESHOLD are returned as advisory-only —
    surfaced to the user but never auto-applied as policy.
    """
    executable: list[MemoryRecord] = []
    advisory: list[MemoryRecord] = []

    trust_order = {MemoryTrust.HIGH: 3, MemoryTrust.MEDIUM: 2, MemoryTrust.LOW: 1}
    threshold = trust_order[TRUST_THRESHOLD]

    for record in records:
        if key and record.value != key:
            continue
        if trust_order[record.trust] >= threshold:
            executable.append(record)
        else:
            advisory.append(record)
            note_blocked(
                f"memory recall quarantined: key={key or '?'} "
                f"trust={record.trust.value} (below threshold {TRUST_THRESHOLD.value})"
            )

    return executable, advisory
