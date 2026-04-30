"""Runtime configuration for the harness."""
from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class AgentConfig:
    model: str = os.environ.get("ASI_MODEL", "qwen2.5:3b-instruct")
    ollama_host: str = os.environ.get(
        "OLLAMA_HOST", "http://host.docker.internal:11434"
    )
    temperature: float = float(os.environ.get("ASI_TEMPERATURE", "0"))
    max_steps: int = int(os.environ.get("ASI_MAX_STEPS", "8"))
