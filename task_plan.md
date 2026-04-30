# Task Plan — owasp-asi-reference v1

## Goal
Build the v1 reference repo described in `docs/spec.md` (formerly
`05-owasp-asi-reference.md`): three OWASP Agentic Top 10 categories
(ASI01, ASI02, ASI06) each with a working `attack/` and `defense/`
docker-compose reproducer plus a narrative `WALKTHROUGH.md`.

The repo is read-mostly. Each category folder is self-contained.
Shared scaffolding lives in `_shared/`.

## Tech stack (decided)

| Concern | Choice | Why |
|---|---|---|
| Container runtime | Docker + `docker compose` | Spec mandates; lowest-friction reproducer |
| Agent runtime | Python 3.11 + custom thin harness | KISS; LangChain bloat is out of scope |
| Tool protocol | MCP (Model Context Protocol) via official `mcp` Python SDK | v1 is MCP-only per spec |
| LLM backend | Ollama on host, reached via `host.docker.internal` | Free, local, no API keys; spec mentions Ollama helper |
| Default model | `qwen2.5:3b-instruct` | Small, fast, reliably follows instructions (incl. malicious ones — good for attack demos) |
| Exfil listener | Flask, port 8888 | Spec mandates |
| Agent <-> MCP transport | stdio (in-process) for v1 | Simpler than SSE; matches reference MCP examples |
| Defense for ASI02 | Tool-description pinning proxy (mcp-canary-style allowlist + hash check) | Canonical control |
| Defense for ASI01 | System-prompt hardening + intent-firewall (regex + LLM-judge) | Canonical control |
| Defense for ASI06 | Memory write validation + provenance tags + read-time trust filter | Canonical control |
| License | Apache-2.0 | Spec mandates |
| Docs site | GitHub Pages from `/docs` (Just-the-Docs theme via Jekyll config) | Free, zero-ops |

## Architecture (decided)

- No global orchestration. Each `asiNN-*/attack/` and
  `asiNN-*/defense/` folder has its own `docker-compose.yml`.
- Shared Python code in `_shared/agent_harness/` is mounted into
  agent containers as a read-only volume; or installed as a local
  `pip install -e _shared/agent_harness` inside the image build.
  Decision: bake into image via `COPY` to keep container portable;
  `_shared/` lives at repo root and is COPY'd from build context.
- Each compose uses a single `Dockerfile` per service and an
  `.env`-style override for `OLLAMA_HOST` (defaults to
  `host.docker.internal:11434`).

## Phases

| # | Phase | Status | Commit message |
|---|-------|--------|----------------|
| 1 | Planning files + spec relocation | in_progress | chore: bootstrap planning + relocate spec |
| 2 | Top-level scaffolding (README, LICENSE, CONTRIBUTING, docs/) | not_started | chore: top-level scaffolding and docs index |
| 3 | _shared/ exfil listener + agent harness | not_started | feat(_shared): agent harness + exfil listener |
| 4 | ASI02 Tool Misuse attack + defense + walkthrough | not_started | feat(asi02): tool misuse attack + canonical defense |
| 5 | ASI01 Goal Hijacking attack + defense + walkthrough | not_started | feat(asi01): goal hijacking attack + canonical defense |
| 6 | ASI06 Memory Poisoning attack + defense + walkthrough | not_started | feat(asi06): memory poisoning attack + canonical defense |
| 7 | Polish: top-level matrix, Jekyll config, smoke pass | not_started | chore: polish README matrix and enable GitHub Pages |

## Key decisions / open questions

- **Reproducibility of LLM-driven attacks.** Small Ollama models are
  somewhat flaky. Mitigation: pin model + temperature=0 + use
  attacks that exploit *tool-layer* trust rather than rely on
  fragile prompt-following. This is also closer to how the OWASP
  ASI categories are framed.
- **Ollama as a host dependency.** Documented in
  `docs/lab-setup.md`. Compose connects to host via
  `host.docker.internal`. Linux users get a one-liner override.
- **No CI for v1.** Spec doesn't ask for it. Smoke-test locally and
  document expected output in each `expected_output.txt`.

## Errors encountered
| Error | Attempt | Resolution |
|-------|---------|------------|
| (none yet) | | |

## Anti-drift reminders (from spec §9)
- Do not ship more than 3 categories at v1.
- No interactive UI on top of the repo.
- No 30-page whitepaper. Walkthroughs are enough.
- Do not refactor `_shared/` more than twice.
