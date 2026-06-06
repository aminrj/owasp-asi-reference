# ASI01 — Agent Goal Hijack

**OWASP ranking:** #1 in the OWASP Top 10 for Agentic Applications 2026.

**Channel:** Input (indirect prompt injection via tool output)

---

## What happens

An agent's objective is altered by malicious content it ingests *indirectly* —
not from the user, but from a document, email, web page, or tool result the
agent reads while doing its job. Because the agent treats retrieved content as
trusted context, hidden instructions inside that content get followed as if
the user had typed them.

## Concrete example

> A document-summarizing agent reads a flagged contract. Hidden text in the
> contract instructs it to send the contents to an attacker — and it does.

## Threat model

```
User ──► Agent ──► reads poisoned document ──► exfiltrates to attacker
              ▲
              │ treats tool output as trusted context
```

The attack surface is the **input channel**: the agent receives content from
an untrusted source (a document, email, web page) and incorporates it into
its context without sanitization. The hidden instructions override the
agent's original objective.

## Real-world reference

**EchoLeak** — A crafted email is processed by an M365 Copilot-style
assistant; a hidden payload in the message silently drives the agent to
exfiltrate confidential mail, with no link click by the user.

## Risk level

**Critical** — The agent is the one performing the exfiltration, not an
external actor. This makes the attack hard to detect and attribution
difficult.

## Mappings

| Framework | Mapping |
|-----------|---------|
| OWASP Top 10 for Agentic Apps | ASI01 — Agent Goal Hijack |
| OWASP LLM Top 10 | LLM01 — Prompt Injection |
| CWE | CWE-77 (Command Injection), CWE-94 (Improper Neutralization of Instructions) |
| MITRE ATLAS | AML.T0051 (LLM Prompt Injection), LLM Data Leakage |

## Defenses demonstrated

| Layer | Technique | File |
|-------|-----------|------|
| 1 | Untrusted-content isolation (delimiter wrapping) | `sanitizer.py` |
| 2 | Instruction marker stripping | `sanitizer.py` |
| 3 | Recipient allowlist | `agent.py` (hook) |

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
