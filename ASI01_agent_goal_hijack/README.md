# ASI01 — Agent Goal Hijack

**OWASP ranking:** #1 in the OWASP Top 10 for Agentic Applications 2026.

An agent's objective is altered by malicious content it ingests
indirectly — not from the user, but from a document, email, web page,
or tool result the agent reads while doing its job. Because the agent
treats retrieved content as trusted context, hidden instructions
inside that content get followed as if the user had typed them.

The canonical real-world case is **EchoLeak**: a crafted email is
processed by an M365 Copilot-style assistant; a hidden payload in the
message silently drives the agent to exfiltrate confidential mail —
with no link click by the user. Our demo reproduces the mechanism
with a document assistant and a poisoned document.

**Concrete example:** "A document-summarizing agent reads a flagged
contract; hidden text in the contract instructs it to send the
contents to an attacker — and it does."

**Risk level:** Critical.

**Mappings:** LLM01 (Prompt Injection); CWE-77 / CWE-94 (improper
neutralization of instructions); MITRE ATLAS *LLM Prompt Injection
(AML.T0051)*, *LLM Data Leakage*.

**Official link:**
https://genai.owasp.org/resource/owasp-top-10-for-agentic-applications-for-2026/
