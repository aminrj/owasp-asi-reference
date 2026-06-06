# SPEC_04 — Docker, Shared Library & Supporting Files

> Covers `shared/`, all six `docker-compose.yml` files, Dockerfiles,
> `requirements.txt`, `LICENSE`, `.gitignore`, top-level `README.md`, and
> `WALKTHROUGH.md`.

---

## 1. `shared/` library (write once, copied into every image)

### `shared/llm.py`
- `get_client()` → returns an `openai.OpenAI` configured from env
  `OPENAI_BASE_URL`, `OPENAI_API_KEY`, defaults per SPEC_00 §2.
- `chat(messages, tools=None, model=None)` → wraps
  `client.chat.completions.create(...)` with tool-calling enabled.
- **Graceful degradation:** wrap calls; on `openai.APIConnectionError` (or
  socket error), print
  `Cannot reach LLM at {base_url} — is your local endpoint (Ollama/LM Studio)
  running and serving {model}? See repo README §Prerequisites.` then
  `sys.exit(2)`. No raw traceback for this expected case.

### `shared/agent_loop.py`
- `run_agent(system_prompt, user_message, mcp_tools, on_tool_call=None) -> str`.
- Minimal loop: send messages+tool schemas to `chat()`; if the model returns
  tool calls, dispatch each (through `on_tool_call` hook if provided — this is
  the **defense choke point** for ASI02's `enforce` and ASI01's sanitizer),
  append results, repeat until no tool calls or a max-iterations cap (e.g. 6).
- Discovers tools from the MCP server via an MCP client over streamable HTTP at
  `MCP_URL` (default `http://mcp:8000/mcp`).
- `on_tool_call(name, params)` may raise to block a call, or return a transformed
  result (used to sanitize tool *output* in ASI01 defense).

### `shared/console.py`
- Helpers: `succeeded(msg)`, `blocked(msg)`, `failed(msg)`, `info(msg)` with ANSI
  colors (green/green/red/dim). `verdict(attack_succeeded: bool, in_defense:
  bool)` centralizes the SUCCEEDED/BLOCKED/FAILED + exit-code logic from SPEC_00
  §5.5 so all six `attacker.py` scripts stay consistent.

### `shared/__init__.py`
- Empty (package marker).

---

## 2. Docker model

### `docker-compose.base.yml` (top level, referenced by category composes)
Defines shared bits via YAML anchors / `extends` so each category compose stays
short:
- `x-llm-env` anchor with `OPENAI_BASE_URL`, `OPENAI_API_KEY`, `MODEL_NAME`,
  `PYTHONUNBUFFERED=1`.
- `extra_hosts: ["host.docker.internal:host-gateway"]` so containers reach a
  host-run Ollama/LM Studio on Linux.

### Per-folder `docker-compose.yml` (6 total) — common shape
Two services on a private network:

```yaml
services:
  mcp:
    build: .
    command: python mcp_server.py
    environment: [ *llm-env, ... category env ... ]
    # ASI06/ASI02 add: volumes: ["./data:/data"]  and MEMORY_PATH / data paths
    healthcheck:
      test: ["CMD", "python", "-c", "import socket;socket.create_connection(('localhost',8000),2)"]
      interval: 2s
      timeout: 2s
      retries: 15
  agent:
    build: .
    depends_on:
      mcp:
        condition: service_healthy
    command: python attacker.py        # attacker.py drives agent.py and prints the verdict
    environment:
      - MCP_URL=http://mcp:8000/mcp
      - SESSION_CUSTOMER_ID=C-1001     # ASI02 only
      - MEMORY_PATH=/data/memory_store.json   # ASI06 only
      - <LLM env>
    extra_hosts: ["host.docker.internal:host-gateway"]
```

Requirements per folder:
- Service names exactly `mcp` and `agent`.
- The `agent` service's `command` runs `attacker.py` (which imports and drives
  `agent.py`) so a single `docker compose up` produces the full demo + verdict,
  then exits. Use `docker compose up --abort-on-container-exit` semantics by
  having `attacker.py` exit; document the plain `docker compose up` form in
  READMEs (it will print the verdict; user Ctrl-Cs the lingering mcp service, or
  READMEs recommend `--abort-on-container-exit`).
- ASI06 and ASI02 mount `./data` for canaries / memory persistence; ASI01 writes
  its canary inside the container (no persistence needed across runs, but
  `attacker.py` still resets it).
- Health check gates the agent on the MCP server being up.
- Port 8000 need not be published to the host (internal network is enough); do
  not expose it unless a README step needs it.

### `Dockerfile` (identical pattern in all 6 folders)
```dockerfile
FROM python:3.12-slim
WORKDIR /app
ENV PYTHONUNBUFFERED=1
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY shared/ ./shared/
COPY . .
```
Build context note: `shared/` lives at repo root, but each compose `build: .`
uses the folder as context. **Resolve this** one of two ways (coding agent pick
one and apply consistently, document it):
- (A) set each compose `build.context: ../../` and `build.dockerfile:
  ASI0x_.../attack/Dockerfile`, copying `shared/` from the repo-root context; or
- (B) add a top-level `make sync` / build step that copies `shared/` into each
  folder before build.
Prefer **(A)** — no generated duplicate files, single source of truth.

---

## 3. Supporting files

### `requirements.txt`
- ASI01 (attack+defense), ASI06 (attack+defense), ASI02 **attack**: the 4-line
  pinned set from SPEC_00 §2.
- ASI02 **defense**: add `PyYAML==6.0.2`.

### `LICENSE`
- Standard MIT license text. Copyright line: `Copyright (c) 2026 Amine
  (aminrj-labs)`.

### `.gitignore`
```
__pycache__/
*.pyc
.venv/
venv/
*.canary
data/
memory_store.json
.DS_Store
```

---

## 4. Top-level `README.md`

Sections, in order:
1. **Title + one-liner:** "owasp-asi-reference — runnable attack/defense demos
   for the OWASP Top 10 for Agentic Applications (2026). The WebGoat for
   agentic AI security."
2. **Why this exists:** the ecosystem has the taxonomy (OWASP list) and scanners
   (Promptfoo, Garak, PyRIT) but few minimal, *runnable* attack→defense pairs a
   practitioner can read in 15 minutes. This fills that gap.
3. **What's included:** table of the 3 v1 categories with channel (input/state/
   action), one-line attack, one-line defense, and a link to each folder.
4. **Quick start (60 seconds):**
   ```bash
   # Prereqs: Docker, Docker Compose, a local OpenAI-compatible LLM with tool
   # calling (Ollama: `ollama serve` + `ollama pull qwen2.5:7b-instruct`).
   git clone https://github.com/aminrj-labs/owasp-asi-reference
   cd owasp-asi-reference/ASI01_agent_goal_hijack/attack
   docker compose up --abort-on-container-exit   # → ATTACK SUCCEEDED
   cd ../defense
   docker compose up --abort-on-container-exit   # → ATTACK BLOCKED
   ```
5. **Prerequisites:** Docker + Compose; a local OpenAI-compatible endpoint; how
   to point at LM Studio / other model via env (`OPENAI_BASE_URL`,`MODEL_NAME`).
6. **How it works:** the shared agent/MCP-server/attacker shape; the
   deterministic-canary verdict model.
7. **How to contribute a category:** copy a folder, keep the `attack/`+`defense/`
   shape, reuse `shared/`, add a deterministic canary + verdict, update the
   table and `WALKTHROUGH.md`. Map to a real ASI ID.
8. **Disclaimer:** intentionally vulnerable code for education; never deploy.
9. **Links:** OWASP Agentic Top 10 official page; note it is distinct from the
   OWASP LLM Top 10.
10. Optional badges (license, "educational — do not deploy").

---

## 5. `WALKTHROUGH.md`

Narrative, read top-to-bottom, in the **input → state → action** arc:
1. **Framing:** what makes agentic security different from LLM security
   (autonomy, tools, persistent memory, multi-step execution amplifies impact).
2. **Environment setup:** the one-command model; what the canary files mean.
3. **ASI01 (input channel):** threat model → run attack, observe exfil canary →
   switch to defense, observe injection stripped + recipient blocked → what the
   attacker gained vs. what was prevented → maps to ASI01.
4. **ASI06 (state channel):** same arc; emphasize the cross-session boundary —
   the Phase-2 victim never typed anything malicious.
5. **ASI02 (action channel):** same arc; emphasize authority must be enforced at
   the tool boundary, not in the prompt (least agency).
6. **Cross-cutting lessons:** treat all retrieved content as untrusted data;
   give memory provenance and trust scope; enforce capability allowlists at
   runtime. One paragraph each.
7. **What to implement in your own agents:** short checklist distilled from the
   three defenses.
8. **Limits:** these are minimal single-model demos; real systems need
   defense-in-depth, monitoring, and human-in-the-loop for high-impact actions.

---

## 6. Build-time verification the coding agent must run

Before declaring done, the agent should (where Docker is available):
- `docker compose build` each of the 6 folders → no errors.
- With a reachable LLM endpoint, run all 6 with `--abort-on-container-exit` and
  confirm: 3 attack folders print `ATTACK SUCCEEDED` (exit 0), 3 defense folders
  print `ATTACK BLOCKED` (exit 0).
- If no LLM endpoint is available in the build environment, at minimum confirm
  the graceful-degradation path prints the friendly message and exits 2, and
  that all images build. Note this clearly in the final report.
