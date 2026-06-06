# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- (none yet)

### Changed

- (none yet)

### Fixed

- (none yet)

---

## [1.0.0] — 2026-06-06

### Initial release

#### Categories

- **ASI01 — Agent Goal Hijack** (input channel)
  - Attack: Indirect prompt injection via poisoned document
  - Defense: Untrusted-content isolation + instruction stripping + recipient allowlist
- **ASI06 — Memory and Context Poisoning** (state channel)
  - Attack: Persistent memory poisoning across sessions
  - Defense: Provenance tagging + trust-scoped recall
- **ASI02 — Tool Misuse and Exploitation** (action channel)
  - Attack: Parameter pollution + tool-chain abuse
  - Defense: Runtime policy enforcement (allowlist + constraints)

#### Architecture

- FastMCP-based MCP server/client transport (replaces ollama harness)
- `openai` SDK for LLM communication (replaces direct ollama calls)
- Deterministic canary verdicts (replaces network exfil listener)
- Shared library: `llm.py`, `agent_loop.py`, `console.py`
- Docker Compose: two-service pattern (`mcp` + `agent`)
- Python 3.12, pinned dependencies

#### Documentation

- Top-level `README.md` with architecture diagram and quickstart
- `WALKTHROUGH.md` — pedagogical arc (input → state → action)
- Category READMEs (OWASP ranking, explanation, example, mappings)
- Per-folder READMEs (run instructions, expected output, verification)
- `CONTRIBUTING.md` — how to add new categories
- `SECURITY.md` — security policy
- `CODE_OF_CONDUCT.md` — contributor covenant

#### Dependencies

- `fastmcp==3.3.1`
- `mcp==1.27.0`
- `openai==1.99.0`
- `pydantic==2.11.7`
- `PyYAML==6.0.2` (ASI02 defense only)

---

## Comparisons

[Unreleased]: https://github.com/aminrj-labs/owasp-asi-reference/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/aminrj-labs/owasp-asi-reference/releases/tag/v1.0.0
