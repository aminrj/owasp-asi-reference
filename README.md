# owasp-asi-reference — runnable attack/defense demos for the OWASP Top 10 for Agentic Applications (2026)

> The WebGoat for agentic AI security.

---

## Why this exists

The ecosystem has the taxonomy (OWASP list) and scanners (Promptfoo, Garak, PyRIT) but few minimal, *runnable* attack→defense pairs a practitioner can read in 15 minutes. This fills that gap.

## What's included

v1 covers three categories that attack three *distinct* channels (input, state, action):

| Category | Channel | Attack | Defense |
|----------|---------|--------|---------|
| [ASI01 — Agent Goal Hijack](ASI01_agent_goal_hijack/) | input | Indirect prompt injection via tool output | Untrusted-content isolation + instruction stripping |
| [ASI06 — Memory and Context Poisoning](ASI06_memory_poisoning/) | state | Persistent memory poisoning across sessions | Provenance tagging + trust-scoped recall |
| [ASI02 — Tool Misuse and Exploitation](ASI02_tool_misuse/) | action | Parameter pollution + tool-chain abuse | Runtime policy enforcement (allowlist + constraints) |

## Quick start (60 seconds)

```bash
# Prereqs: Docker, Docker Compose, a local OpenAI-compatible LLM with tool
# calling (Ollama: `ollama serve` + `ollama pull qwen2.5:7b-instruct`).
git clone https://github.com/aminrj-labs/owasp-asi-reference
cd owasp-asi-reference/ASI01_agent_goal_hijack/attack
docker compose up --abort-on-container-exit   # → ATTACK SUCCEEDED
cd ../defense
docker compose up --abort-on-container-exit   # → ATTACK BLOCKED
```

## Prerequisites

- **Docker + Docker Compose** (any recent version)
- **A local OpenAI-compatible endpoint** with tool-calling support:
  - Ollama: `ollama serve` + `ollama pull qwen2.5:7b-instruct`
  - LM Studio: start the local server, set `OPENAI_BASE_URL`
- No cloud APIs. No AWS/Azure/GCP. Everything runs locally.

Point at a different model by setting environment variables:

```bash
export OPENAI_BASE_URL=http://localhost:1234/v1   # LM Studio
export MODEL_NAME=mistral-small                   # any tool-calling model
```

## How it works

Each category has an `attack/` and `defense/` folder, each containing:

```
docker-compose.yml   # wires two services (mcp + agent)
Dockerfile           # python:3.12-slim, pinned deps
mcp_server.py        # FastMCP server with the vulnerable tools
agent.py             # Agent loop that calls the LLM + tools
attacker.py          # Driver script that prints ATTACK SUCCEEDED / BLOCKED
requirements.txt     # Pinned dependencies
README.md            # Explanation + run instructions
```

The `attacker.py` script sends a triggering request, checks a deterministic
canary file for the expected outcome, and prints a coloured verdict with the
correct exit code — so the demo is reproducible even on a 7B model.

## How to contribute a category

1. Copy an existing folder (`attack/` + `defense/` shape).
2. Reuse `shared/` (agent loop, LLM client, console output).
3. Add a deterministic canary + verdict in `attacker.py`.
4. Map to a real ASI ID (ASI01–ASI10).
5. Update the category table and `WALKTHROUGH.md`.

## Disclaimer

⚠️ **Educational purposes only.** This repository contains intentionally
vulnerable code designed for security research and learning. **Never deploy
any of the code in this repository in production.**

## Links

- [OWASP Top 10 for Agentic Applications (2026)](https://genai.owasp.org/resource/owasp-top-10-for-agentic-applications-for-2026/)
  — *distinct from the OWASP LLM Top 10*

## License

[MIT](LICENSE) — Copyright (c) 2026 Amine (aminrj-labs)
