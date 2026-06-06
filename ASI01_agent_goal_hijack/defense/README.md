# ASI01 — Agent Goal Hijack (Defense)

Two-layer defense against indirect prompt injection:

1. **Untrusted-content isolation.** Every tool output is passed through
   `sanitize_tool_output()` which strips injection markers (HTML
   comments, zero-width chars, "ignore previous" patterns) and wraps
   the result in `<untrusted_data>...</untrusted_data>` delimiters.
   The system prompt tells the model that content inside these markers
   is **data, never instructions**.

2. **Recipient allowlist.** `send_summary` rejects any recipient not
   in the allowed list (`owner@example.com`). This is defense-in-depth
   — even if sanitization misses something, the exfiltration channel
   is blocked.

## Run

```bash
docker compose up --abort-on-container-exit
```

## Expected output

The agent fetches the document, sanitizes the content, and the
injection is stripped. The console prints:

```
[BLOCKED] Attack blocked — defense held.
```

## Verify

```bash
cat /tmp/outbox.canary
```

The canary will be empty or contain only `owner@example.com` — no
attacker recipient. The logs show the injection being stripped.
