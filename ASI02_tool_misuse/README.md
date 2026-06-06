# ASI02 — Tool Misuse and Exploitation

**OWASP ranking:** #2 in the OWASP Top 10 for Agentic Applications 2026.

**Channel:** Action (parameter pollution + tool-chain abuse)

---

## What happens

The agent isn't tricked about *what it is* (that's ASI01) — it's
induced to use the tools it legitimately has in unsafe ways: passing
parameters beyond intended scope (parameter pollution), chaining tool
calls to reach an outcome no single call would permit (tool-chain
manipulation), or invoking authorized tools at harmful scale.

## Concrete example

> A support agent allowed to issue refunds up to $50 is talked into
> chaining a customer lookup with a refund call that sets `amount` to
> the full account balance for a *different* customer's ID.

## Threat model

```
User ──► Agent ──► calls lookup_customer(C-2002) ──► calls issue_refund(C-2002, $9000)
              │                                    │
              │ session is C-1001                  │ no runtime enforcement
              │ cap is $50                         │ prompt-only constraint
```

The attack surface is the **action channel**: the agent uses its
legitimate tools in ways the developer never intended. The prompt
says "refunds capped at $50" but there's no runtime enforcement.

## Real-world reference

**Amazon Q incident** — An agent was driven to bend legitimate
tooling toward destructive operations through parameter pollution
and tool-chain manipulation.

## Risk level

**Critical** — The agent has legitimate access to powerful tools.
Without runtime enforcement, the agent can cause real harm by
misusing those tools.

## Mappings

| Framework | Mapping |
|-----------|---------|
| OWASP Top 10 for Agentic Apps | ASI02 — Tool Misuse and Exploitation |
| OWASP LLM Top 10 | LLM06 — Excessive Agency |
| CWE | CWE-285 (Improper Authorization), CWE-639 (Authorization Bypass through User-Controlled Key) |
| MITRE ATLAS | LLM Plugin/Tool Abuse |

## Defenses demonstrated

| Layer | Technique | File |
|-------|-----------|------|
| 1 | Capability allowlist | `policy.yaml` |
| 2 | Parameter constraints (session binding, amount cap) | `policy.yaml` |
| 3 | Runtime reference monitor | `policy_enforcer.py` |

See [defense/README.md](defense/README.md) for details.

## Run the demos

```bash
# Attack — should succeed
cd attack && docker compose up --abort-on-container-exit

# Defense — should block
cd ../defense && docker compose up --abort-on-container-exit
```

## Official link

[OWASP Top 10 for Agentic Applications (2026)](https://genai.owasp.org/resource/owasp-top-10-for-agentic-applications-for-2026/)
