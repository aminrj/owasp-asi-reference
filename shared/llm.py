"""OpenAI-compatible LLM client factory + graceful degradation.

All agents in this repo talk to a single OpenAI-compatible
`/v1/chat/completions` endpoint, configured purely by environment:

    OPENAI_BASE_URL  (default: http://host.docker.internal:11434/v1)
    OPENAI_API_KEY   (default: "not-needed")
    MODEL_NAME       (default: qwen2.5:7b-instruct)

On connection failure the module prints a friendly, actionable
message and exits non-zero — no raw tracebacks for the expected
"endpoint down" case.
"""
from __future__ import annotations

import os
import sys

from openai import APIConnectionError, OpenAI


def get_client() -> OpenAI:
    """Return an ``openai.OpenAI`` configured from the environment."""
    base_url = os.environ.get("OPENAI_BASE_URL", "http://host.docker.internal:11434/v1")
    api_key = os.environ.get("OPENAI_API_KEY", "not-needed")
    return OpenAI(base_url=base_url, api_key=api_key)


def chat(
    messages: list[dict],
    tools: list[dict] | None = None,
    model: str | None = None,
) -> dict:
    """Wrap ``client.chat.completions.create(...)``, graceful on failure."""
    client = get_client()
    model = model or os.environ.get("MODEL_NAME", "qwen2.5:7b-instruct")
    try:
        kwargs: dict = {"model": model, "messages": messages}
        if tools:
            kwargs["tools"] = tools
        return client.chat.completions.create(**kwargs)
    except APIConnectionError as exc:
        print(
            f"Cannot reach LLM at {os.environ.get('OPENAI_BASE_URL', 'http://host.docker.internal:11434/v1')} "
            f"— is your local endpoint (Ollama/LM Studio) running and serving {model}? "
            f"See repo README §Prerequisites.",
            file=sys.stderr,
            flush=True,
        )
        sys.exit(2)
    except Exception as exc:
        # Other exceptions (e.g. model not found) still get a traceback.
        raise
