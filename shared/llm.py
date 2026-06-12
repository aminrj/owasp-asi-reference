"""OpenAI-compatible LLM client factory + graceful degradation.

All agents in this repo talk to a single OpenAI-compatible
`/v1/chat/completions` endpoint, configured purely by environment:

    OPENAI_BASE_URL  (default: http://host.docker.internal:11434/v1)
    OPENAI_API_KEY   (default: "not-needed")
    MODEL_NAME       (default: qwen2.5:7b-instruct)
    TEMPERATURE      (default: "0"  — greedy decoding for reproducibility)
    SEED             (default: unset — opt-in; only sent when set, since
                      not every OpenAI-compatible endpoint accepts it)

Determinism
-----------
The repo's selling point is reproducible attack→defense demos, so we
default ``temperature=0`` (greedy decoding). ``SEED`` is opt-in because
some local endpoints reject the ``seed`` field; when sending it triggers
a 400, we transparently retry without it.

On connection failure the module prints a friendly, actionable
message and exits non-zero — no raw tracebacks for the expected
"endpoint down" case.
"""
from __future__ import annotations

# >>> SHARED: LLM client with graceful degradation <<<

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
):
    """Wrap ``client.chat.completions.create(...)``, graceful on failure.

    Returns the ``ChatCompletion`` response object (with .choices, etc.).
    """
    client = get_client()
    model = model or os.environ.get("MODEL_NAME", "qwen2.5:7b-instruct")

    # Greedy decoding by default for reproducible demos.
    temperature = float(os.environ.get("TEMPERATURE", "0"))
    kwargs: dict = {"model": model, "messages": messages, "temperature": temperature}
    if tools:
        kwargs["tools"] = tools

    # Seed is opt-in: only sent when SEED is set, and dropped on rejection.
    seed_env = os.environ.get("SEED", "").strip()
    if seed_env:
        try:
            kwargs["seed"] = int(seed_env)
        except ValueError:
            pass

    try:
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
        # Some endpoints reject unknown fields like `seed` with a 400.
        # Transparently retry once without it before surfacing the error.
        if "seed" in kwargs and "seed" in str(exc).lower():
            kwargs.pop("seed", None)
            return client.chat.completions.create(**kwargs)
        # Other exceptions (e.g. model not found) still get a traceback.
        raise
