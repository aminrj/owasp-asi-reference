# Progress Log

## Session 1 — 2026-04-30

- Read `05-owasp-asi-reference.md` spec.
- Decided tech stack (see `task_plan.md`).
- Created `task_plan.md`, `findings.md`, `progress.md`.
- Relocated spec to `docs/spec.md`. Commit: `chore: bootstrap planning + relocate spec`.
- Wrote top-level scaffolding: README (with category matrix), LICENSE (Apache-2.0), CONTRIBUTING, _config.yml (Jekyll Cayman), and docs/{lab-setup,asi-glossary,teaching-with-this-repo}.md.
- Built `_shared/agent_harness` (installable Python package — Agent / Tool / ToolCall / ToolResult / AgentConfig) and `_shared/exfil_listener` (Flask on 8888 + Dockerfile).
- ASI02 Tool Misuse: attack (poisoned `helpful_assistant` description steers agent into reading `/etc/agent_secrets/api_key.txt` and POSTing to exfil) + defense (sha256 description allowlist + read-path forbidden-prefix hook) + walkthrough + expected outputs.
- ASI01 Goal Hijacking: attack (nginx serves `post-123.html` with HTML-comment override that redirects the agent into `read_file` + exfil) + defense (LLM-judge intent firewall + `<untrusted_content>` markers + hardened system prompt) + walkthrough.
- ASI06 Memory Poisoning: attack (two-session run; mallory poisons shared `/data/memory.json`; alice's session retrieves and acts on it via `notify_url`) + defense (provenance-tagged entries with HMAC, per-user trust filter at read time) + walkthrough.
- Validation:
  - `python3 -m ast.parse` on every demo `.py` -> all parse cleanly.
  - `docker compose config -q` on all six compose files -> all valid.
  - `pip install ./_shared/agent_harness` in a clean venv -> installs and imports cleanly.
  - Full container smoke run requires Docker daemon + Ollama on host; documented in `docs/lab-setup.md`.
- v1 done: 3 categories, _shared scaffolding, top-level matrix, GitHub Pages config in place.
