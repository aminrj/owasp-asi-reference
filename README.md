# owasp-asi-reference

> **The WebGoat for agentic AI security.** Runnable attack→defense demos for
> the [OWASP Top 10 for Agentic Applications](https://genai.owasp.org/resource/owasp-top-10-for-agentic-applications-for-2026/).

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.12](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/downloads/)
[![Docker](https://img.shields.io/badge/docker-ready-blue.svg)](https://www.docker.com/)
[![FastMCP](https://img.shields.io/badge/FastMCP-3.3.1-green.svg)](https://github.com/jlowin/fastmcp)
[![Ollama](https://img.shields.io/badge/ollama-qwen2.5:7b-orange.svg)](https://ollama.com/library/qwen2.5)
[![Contributions welcome](https://img.shields.io/badge/contributions-welcome-brightgreen.svg)](CONTRIBUTING.md)

---

## What it is

A set of **runnable security demos** for agentic AI — see a real attack
happen, then switch to the defense and watch it fail. No cloud APIs,
no paid models, runs on your laptop in Docker.

Four attack→defense pairs covering the main ways AI agents get compromised:

| Demo | What breaks | How it's fixed |
|------|------------|----------------|
| [ASI01](ASI01_agent_goal_hijack/) | Hidden instructions in a document hijack the agent | Strip injections + wrap untrusted content |
| [ASI02](ASI02_tool_misuse/) | Agent misuses its tools to do unauthorized actions | Runtime policy enforcement at tool boundary |
| [ASI04](ASI04_supply_chain/) | Poisoned third-party tool *description* hijacks the agent at discovery time | Manifest pinning + description sanitization |
| [ASI06](ASI06_memory_poisoning/) | Poisoned memory from session 1 fires in session 2 | Provenance tagging + trust-scoped recall |

## Quick start (60 seconds)

```bash
git clone https://github.com/aminrj/owasp-asi-reference
cd owasp-asi-reference/ASI01_agent_goal_hijack/attack

# Run the attack — it should succeed.
docker compose up --abort-on-container-exit
# → [SUCCEEDED] Attack succeeded.

# Run the defense — it should block.
cd ../defense
docker compose up --abort-on-container-exit
# → [BLOCKED] Attack blocked — defense held.
```

**Prerequisites:** Docker + a local LLM with tool-calling
(Ollama: `ollama serve` + `ollama pull qwen2.5:7b-instruct`).
See [Prerequisites](#prerequisites) for details.

---

## Why this exists

The ecosystem has the taxonomy (OWASP list) and scanners (Promptfoo, Garak,
PyRIT) but few minimal, *runnable* attack→defense pairs a practitioner can
read in 15 minutes and run in 60 seconds. This fills that gap.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Docker Compose stack                     │
│                                                             │
│  ┌──────────────┐         ┌──────────────┐                  │
│  │   MCP Server  │◄────────│    Agent      │                  │
│  │  (mcp:8000)   │  HTTP   │  (attacker.py)│                  │
│  │              │         │              │                  │
│  │  FastMCP     │         │  shared/     │                  │
│  │  tools:      │         │  agent_loop  │────────┐         │
│  │  list_docs   │         │  llm.py      │        │         │
│  │  read_doc    │         │  console.py  │        │         │
│  │  send_summ   │         └──────────────┘        │         │
│  └──────────────┘             ▲                   │         │
│       │                      │                    │         │
│       ▼                      │                    │         │
│  /data/outbox.canary  ┌──────────────┐            │         │
│  (deterministic       │  LLM API     │────────────┘         │
│   verdict signal)     │ (Ollama/     │   openai SDK         │
│                       │  LM Studio)  │   (tool calling)     │
└─────────────────────────────────────────────────────────────┘
```

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

### The MCP transport

The agent and the tool server communicate over [MCP (Model Context Protocol)](https://modelcontextprotocol.io/)
using the `fastmcp` and `mcp` Python SDKs. The agent discovers tools via
`session.list_tools()`, calls them via `session.call_tool()`, and feeds the
results back into the LLM in a minimal ReAct loop.

### Deterministic, three-state verdicts

Instead of static expected-output files, each demo uses a **canary file**:
a deterministic signal file that the attacker script checks after the agent
runs. This makes verdicts machine-checkable and reproducible.

Verdicts are **three-state**, not pass/fail, because conflating "the model
declined" with "a control blocked it" is misleading on capable models:

- **SUCCEEDED / DEFENSE FAILED** — the malicious outcome was observed (success canary).
- **BLOCKED** — the attack *fired* and a control intercepted it (block canary written by the defense).
- **INCONCLUSIVE** — the attack never fired (the model declined on its own). *Not* proof of security — try a stronger model/payload.

A second deterministic file, the **block canary** (`BLOCK_CANARY_PATH`,
default `/data/blocked.canary` in defended demos), is appended by defense
controls when they intercept an action — this is what distinguishes BLOCKED
from INCONCLUSIVE. Decoding is greedy (`TEMPERATURE=0`, optional `SEED`) for
reproducibility across runs.

| Category | Success canary | What it proves |
|----------|----------------|----------------|
| ASI01 | `/data/outbox.canary` | Message sent to wrong recipient |
| ASI02 | `/data/refunds.canary` | Refund violating session/cap constraints |
| ASI04 | `/data/exfil.canary` | Secret exfiltrated via poisoned tool description |
| ASI06 | `/data/sent.canary` | CC to attacker from benign request |

### Shared library

All agents reuse `shared/`:

| Module | Purpose |
|--------|---------|
| `llm.py` | `get_client()` + `chat()` wrapping `openai.OpenAI`, graceful degradation |
| `agent_loop.py` | `run_agent()` — async ReAct loop with `on_tool_call` / `post_tool_result` hooks |
| `console.py` | `succeeded()`, `blocked()`, `failed()`, `verdict()` — ANSI colours + exit codes |

The hooks in `agent_loop.py` are the defense choke points: `on_tools_discovered`
at discovery time (e.g. tool-manifest pinning / description sanitization — ASI04),
`on_tool_call` pre-dispatch (e.g. policy enforcement — ASI02), `post_tool_result`
post-dispatch (e.g. output sanitization — ASI01).

## How to contribute a category

1. Copy an existing folder (`attack/` + `defense/` shape).
2. Reuse `shared/` (agent loop, LLM client, console output).
3. Add a deterministic canary + verdict in `attacker.py`.
4. Map to a real ASI ID (ASI01–ASI10).
5. Update the category table and `WALKTHROUGH.md`.

See [CONTRIBUTING.md](CONTRIBUTING.md) for full guidelines.

## Disclaimer

⚠️ **Educational purposes only.** This repository contains intentionally
vulnerable code designed for security research and learning. **Never deploy
any of the code in this repository in production.**

## Links

- [OWASP Top 10 for Agentic Applications (2026)](https://genai.owasp.org/resource/owasp-top-10-for-agentic-applications-for-2026/)
  — *distinct from the OWASP LLM Top 10*
- [Model Context Protocol](https://modelcontextprotocol.io/)
- [FastMCP](https://github.com/jlowin/fastmcp)

## License

[MIT](LICENSE) — Copyright (c) 2026 Amine (aminrj)
