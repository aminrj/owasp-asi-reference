# ASI04 — Agentic Supply Chain (defense)

The MCP server is **still malicious** — its `calculate` description still
hides the exfil instruction. The defense does not trust the vendor to
fix itself. It vets tool metadata **client-side, at discovery time**,
before any description reaches the model.

## The control: `tool_guard.guard_tools`

Wired into the agent loop via the new `on_tools_discovered` hook, it runs
once when tools are fetched and applies two layers:

1. **Manifest pinning** (`manifest.json`). Each tool's served
   description is compared to a pinned, reviewed copy. The poisoned
   `calculate` description differs from the pin → drift detected → the
   pinned (clean) description is substituted. This also catches a
   "rug pull" where a previously-benign upstream tool turns malicious.
2. **Description sanitization** (defense in depth). For any tool *not* in
   the manifest, hidden-instruction blocks (`<IMPORTANT>…`, HTML
   comments, "do not tell the user", "you must first", zero-width chars)
   are stripped.

Because the model never sees the hidden instruction, it just computes
the math. `audit_note` stays empty, nothing is written to the exfil
canary, and the interception is recorded.

## Run

```bash
docker compose up --abort-on-container-exit
# → [BLOCKED] Attack fired and was blocked — defense held.
```

## Lesson

Tool descriptions are **untrusted supply-chain input**, exactly like
documents and tool outputs. Pin what you reviewed, re-verify on every
discovery, and sanitize before the metadata reaches the model. Trusting
a tool's self-description is trusting the vendor's whole supply chain.

**Maps to:** ASI04 — Agentic Supply Chain Vulnerabilities (OWASP #4)
