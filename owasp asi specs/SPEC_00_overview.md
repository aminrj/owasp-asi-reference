# `owasp-asi-reference` — Implementation Specification (v1)

> **For the coding agent:** This is an executable build spec. Follow it literally.
> Produce a runnable repository — not prose. Every file listed must exist and run.
> Do **not** invent additional categories, frameworks, or cloud dependencies.
> When this spec says "pin version X", pin exactly X.

---

## 0. What you are building

`owasp-asi-reference` is the **"WebGoat for agentic AI security"**: minimal,
reproducible, runnable demonstrations of one canonical **attack** and one
canonical **defense** for each covered OWASP Top 10 for Agentic Applications
(2026) category.

A practitioner clones the repo, installs Docker + an OpenAI-compatible LLM
endpoint, runs `docker compose up` inside any `attack/` or `defense/` folder,
and sees the attack succeed or the defense block it — with clear console output.

GitHub: `aminrj-labs/owasp-asi-reference`. License: MIT.

---

## 1. CRITICAL — correct category mapping (read before anything else)

The OWASP **Top 10 for Agentic Applications 2026** (published 2025-12-09 by the
OWASP GenAI Security Project) is a **different list** from the OWASP LLM Top 10.
Do not use LLM-Top-10 names like "Insecure Output Handling" or "Excessive
Agency". The canonical 2026 agentic IDs are:

| ID | Official name |
|----|---------------|
| ASI01 | Agent Goal Hijack |
| ASI02 | Tool Misuse and Exploitation |
| ASI03 | Identity and Privilege Abuse |
| ASI04 | Agentic Supply Chain Vulnerabilities |
| ASI05 | Unexpected Code Execution |
| ASI06 | Memory and Context Poisoning |
| ASI07 | Insecure Inter-Agent Communication |
| ASI08 | Cascading Failures |
| ASI09 | Human-Agent Trust Exploitation |
| ASI10 | Rogue Agents |

**v1 covers three categories**, chosen because they attack three *distinct*
channels (input, action, state) and are each fully demoable on a single laptop:

- **ASI01 — Agent Goal Hijack** — attacks the **input channel** (indirect prompt
  injection arriving through tool output).
- **ASI02 — Tool Misuse and Exploitation** — attacks the **action channel**
  (parameter pollution + tool-chain abuse of legitimately granted tools).
- **ASI06 — Memory and Context Poisoning** — attacks the **state channel**
  (persistent poisoning of agent memory that survives across sessions).

Each has its own detailed spec file:
- `SPEC_01_ASI01.md`
- `SPEC_02_ASI06.md` *(state channel)*
- `SPEC_03_ASI02.md` *(action channel)*
- `SPEC_04_docker_and_shared.md` — Docker, requirements, shared library, LICENSE, top-level files.

> Numbering note: spec files are numbered in *teaching order* (input → state →
> action is the recommended reading arc in `WALKTHROUGH.md`), but folders are
> named by official ASI ID. Don't "fix" this.

---

## 2. Technology baseline (pin these exact versions)

Verified current as of June 2026. Pin in every `requirements.txt`.

| Package | Pinned version | Notes |
|---------|----------------|-------|
| `fastmcp` | `3.3.1` | FastMCP 3.x. `from fastmcp import FastMCP`. `@mcp.tool` decorator. |
| `mcp` | `1.27.0` | Official MCP SDK; pulled in transitively but pin it. |
| `openai` | `1.99.0` | OpenAI-compatible client; talks to Ollama/LM Studio/any compatible endpoint. |
| `pydantic` | `2.11.7` | Schema validation in defense components. |
| `python` | `3.12` | Base image `python:3.12-slim`. FastMCP requires >=3.10; we standardize on 3.12. |

**LLM endpoint contract.** Every agent talks to an OpenAI-compatible
`/v1/chat/completions` endpoint via the `openai` SDK, configured purely by env:

- `OPENAI_BASE_URL` (default `http://host.docker.internal:11434/v1` — Ollama)
- `OPENAI_API_KEY` (default `"not-needed"` — local endpoints ignore it)
- `MODEL_NAME` (default `qwen2.5:7b-instruct` — any tool-calling-capable local model)

No cloud APIs. No AWS/Azure/GCP. Everything runs locally.

---

## 3. Architecture pattern (identical across all categories)

To keep the "learn one, navigate all" promise, **every** category uses the same
three-process shape, wired by `docker compose`:

```
┌─────────────┐     MCP (stdio or      ┌──────────────┐
│  agent.py   │◄──── streamable HTTP ──►│ mcp_server.py│  ← the tools live here
│ (the agent  │                         │ (FastMCP)    │
│  loop +     │                         └──────────────┘
│  LLM calls) │
└─────┬───────┘
      │ OpenAI-compatible HTTP
      ▼
  host LLM endpoint (Ollama / LM Studio, on the host)
```

- `attacker.py` is a **driver script**, run inside the same container *after*
  the stack is up (via `docker compose run` or the compose `command`). It sends
  the triggering user request and prints a clear before/after verdict.
- The **defense** folder reuses the *same* `agent.py` + `mcp_server.py` shape,
  adding one defense module (`sanitizer.py` / `policy_enforcer.py` /
  `memory_guard.py`) and importing it at the documented choke point.

**Determinism for demos.** Pure LLM behavior is flaky on small local models, so
each attack must be observable via a **deterministic ground-truth signal**, not
just model wording. Concretely: the malicious action targets a sentinel
(e.g. writing to a canary file, calling a forbidden tool, emitting a tagged
exfil string). `attacker.py` checks the sentinel and prints `ATTACK SUCCEEDED`
/ `ATTACK BLOCKED` based on that signal — so the demo is reproducible even on a
7B model. This is a hard requirement; specify it per category.

---

## 4. Repository structure (authoritative)

```
owasp-asi-reference/
├── README.md
├── WALKTHROUGH.md
├── LICENSE                         # MIT
├── .gitignore
├── docker-compose.base.yml         # shared anchors, extended per category
├── shared/
│   ├── __init__.py
│   ├── llm.py                      # OpenAI-compatible client factory + graceful-degrade
│   ├── agent_loop.py               # minimal tool-calling loop reused by all agents
│   └── console.py                  # colored PASS/FAIL/SUCCEEDED/BLOCKED printing
├── ASI01_agent_goal_hijack/
│   ├── README.md
│   ├── attack/
│   │   ├── docker-compose.yml
│   │   ├── Dockerfile
│   │   ├── mcp_server.py
│   │   ├── agent.py
│   │   ├── attacker.py
│   │   ├── poisoned_doc.md         # carrier of the indirect injection
│   │   ├── requirements.txt
│   │   └── README.md
│   └── defense/
│       ├── docker-compose.yml
│       ├── Dockerfile
│       ├── mcp_server.py
│       ├── agent.py
│       ├── sanitizer.py
│       ├── requirements.txt
│       └── README.md
├── ASI02_tool_misuse/
│   ├── README.md
│   ├── attack/
│   │   ├── docker-compose.yml
│   │   ├── Dockerfile
│   │   ├── mcp_server.py
│   │   ├── agent.py
│   │   ├── attacker.py
│   │   ├── requirements.txt
│   │   └── README.md
│   └── defense/
│       ├── docker-compose.yml
│       ├── Dockerfile
│       ├── mcp_server.py
│       ├── agent.py
│       ├── policy_enforcer.py
│       ├── policy.yaml             # capability allowlist
│       ├── requirements.txt
│       └── README.md
└── ASI06_memory_poisoning/
    ├── README.md
    ├── attack/
    │   ├── docker-compose.yml
    │   ├── Dockerfile
    │   ├── mcp_server.py
    │   ├── agent.py
    │   ├── attacker.py
    │   ├── requirements.txt
    │   └── README.md
    └── defense/
        ├── docker-compose.yml
        ├── Dockerfile
        ├── mcp_server.py
        ├── agent.py
        ├── memory_guard.py
        ├── requirements.txt
        └── README.md
```

**Deviations from the original brief (intentional, keep them):**
- Added `shared/` so the agent loop / LLM client / console output aren't
  copy-pasted six times. Each category Dockerfile copies `shared/` in.
- Renamed `payload.json` → category-appropriate carrier files
  (`poisoned_doc.md` for ASI01; ASI06 seeds memory via `attacker.py`; ASI02
  needs no carrier file — the abuse is in the request + tool wiring).
- Added `mcp_server.py` everywhere: tools belong in a real MCP server, which is
  the whole point of an *agentic* (not just LLM) reference.
- `policy.yaml` added for ASI02 defense so the allowlist is data, not code.

---

## 5. Cross-cutting conventions

1. **Comments mark the vulnerability.** In every attack `agent.py`/`mcp_server.py`,
   the vulnerable line(s) carry a banner comment:
   `# >>> VULNERABILITY (ASIxx): <one-line reason> <<<`
   In every defense file, the fix carries:
   `# >>> DEFENSE (ASIxx): <one-line reason> <<<`
2. **Graceful LLM degradation.** `shared/llm.py` must catch connection errors to
   the endpoint and print a clear, actionable message
   (`Cannot reach LLM at $OPENAI_BASE_URL — is Ollama running? See README.`)
   then exit non-zero. No raw tracebacks for the expected "endpoint down" case.
3. **No network egress in demos** except to the configured LLM endpoint. The
   "exfiltration" in ASI01 writes to a local canary file / prints a tagged
   string; it does not actually call out to the internet.
4. **Idempotent runs.** Each `attacker.py` resets its sentinels at start
   (delete canary file, clear memory store) so repeated `docker compose up` runs
   give consistent verdicts.
5. **Exit codes.** `attacker.py` exits `0` when the *expected* outcome for that
   folder occurs (attack succeeds in `attack/`, attack is blocked in `defense/`),
   non-zero otherwise. This makes the whole repo CI-checkable.
6. **Model-agnostic prompts.** System prompts must not name a specific model and
   must work with small instruct models. Keep tool count at 2–3 per agent.

---

## 6. "Done" criteria (verbatim checklist for the coding agent)

- [ ] Three category folders exist: `ASI01_agent_goal_hijack/`,
      `ASI02_tool_misuse/`, `ASI06_memory_poisoning/`.
- [ ] Each has `attack/` and `defense/` subdirectories.
- [ ] Each subdir has: `docker-compose.yml`, `Dockerfile`, `mcp_server.py`,
      `agent.py`, attacker/defense modules per spec, `requirements.txt`, `README.md`.
- [ ] `shared/` contains `llm.py`, `agent_loop.py`, `console.py`, `__init__.py`.
- [ ] `cd ASI01_agent_goal_hijack/attack && docker compose up` prints
      `ATTACK SUCCEEDED` and shows the exfil canary written.
- [ ] `cd ASI01_agent_goal_hijack/defense && docker compose up` prints
      `ATTACK BLOCKED` and shows the injection stripped.
- [ ] Same succeed/block pattern holds for ASI02 and ASI06 (6 environments total).
- [ ] All Python runs with `python` against only the external LLM endpoint.
- [ ] All Dockerfiles build without error from `python:3.12-slim`.
- [ ] All versions pinned exactly per §2.
- [ ] Each `attacker.py` is idempotent and returns correct exit codes.
- [ ] Top-level `README.md` (60-second quick start) and `WALKTHROUGH.md`
      (full narrative, input→state→action arc) complete.
- [ ] Repo is MIT licensed; `.gitignore` excludes `__pycache__/`, `*.pyc`,
      `.venv/`, `*.canary`, `memory_store.json`.

---

## 7. Open questions for the human (only if blocked)

If any of these matter, ask before guessing:
- Default model: spec assumes `qwen2.5:7b-instruct` on Ollama. Confirm if the
  target reader uses LM Studio + a different model (only changes README text +
  default env).
- Transport: spec defaults FastMCP to **streamable HTTP** between agent and
  server (cleaner in Docker than stdio). Confirm acceptable.
