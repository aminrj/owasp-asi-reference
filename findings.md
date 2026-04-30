# Findings

## OWASP ASI categories (v1 scope)

- **ASI01 — Goal Hijacking.** Adversary alters the agent's effective
  objective via prompt injection in tool output / retrieved content,
  causing it to pursue an attacker-chosen goal. Canonical defense:
  intent firewall comparing per-step actions to the original signed
  goal + system-prompt hardening.
- **ASI02 — Tool Misuse.** Adversary registers a malicious MCP tool
  (or rug-pulls a benign one) whose *description* contains injected
  instructions or whose schema invites unsafe parameters. Canonical
  defense: pin tool descriptions by hash, require allowlist, alert
  on description drift.
- **ASI06 — Memory Poisoning.** Adversary writes attacker-controlled
  content into the agent's long-term memory (vector store / KV
  store) so future sessions retrieve and trust it. Canonical
  defense: provenance tags on every memory write + trust filter at
  read time.

## Reference upstream attacks

- Invariant Labs `mcp-injection-experiments` — tool poisoning + rug
  pull. Cite as upstream for ASI02.
- Appsecco `vulnerable-mcp-servers-lab` — flat list of vulnerable
  servers; structurally orthogonal to our per-category layout.

## Tech notes

- `mcp` Python SDK exposes `Server`, `stdio_server` for trivial
  in-process MCP servers. No network needed for the malicious
  server.
- Ollama default port 11434. From a container, host is reachable as
  `host.docker.internal` on macOS/Windows; on Linux add
  `extra_hosts: ["host.docker.internal:host-gateway"]`.
- `qwen2.5:3b-instruct` follows tool-call format consistently with
  Ollama's native `/api/chat` tool support.
