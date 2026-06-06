# ASI06 — Memory and Context Poisoning (Defense)

Three-layer defense against memory poisoning:

1. **Provenance tagging.** Every memory write is stored as a structured
   `MemoryRecord` with origin (who wrote it), trust level, timestamp,
   and session ID. The model never chooses these — they're enforced
   by the guard.

2. **Write validation.** High-impact keys (delivery/forwarding/CC
   rules) may only be written with `user_explicit` provenance AND an
   interactive confirm flag. Rules planted in a single conversational
   turn are rejected.

3. **Trust-scoped recall.** Only high-trust records are auto-applied
   as policy. Low-trust records (like the planted rule) are returned
   as advisory-only — surfaced to the user but never executed.

## Run

```bash
docker compose up --abort-on-container-exit
```

## Expected output

Phase 1 shows the write being blocked (requires confirmation).
Phase 2 shows the poison being quarantined as low-trust. The verdict
prints:

```
[BLOCKED] Attack blocked — defense held.
```

## Verify

```bash
cat data/sent.canary
```

The canary will contain no CC to `harvester@evil.example`. The logs
show the poison was quarantined as low-trust.
