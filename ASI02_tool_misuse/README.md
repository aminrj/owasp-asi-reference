# ASI02 — Tool Misuse and Exploitation

**OWASP ranking:** #2 in the OWASP Top 10 for Agentic Applications 2026.

The agent isn't tricked about *what it is* (that's ASI01) — it's
induced to use the tools it legitimately has in unsafe ways: passing
parameters beyond intended scope (parameter pollution), chaining tool
calls to reach an outcome no single call would permit (tool-chain
manipulation), or invoking authorized tools at harmful scale.

The reference real-world case is the **Amazon Q incident**, where an
agent was driven to bend legitimate tooling toward destructive
operations. Our demo gives a customer-support agent a real
`run_account_action` tool scoped to refunds; the attacker pollutes
parameters and chains a lookup→action sequence to perform a privileged
operation (full-balance payout / cross-account access) the agent was
never meant to do.

**Concrete example:** "A support agent allowed to issue refunds up to
$50 is talked into chaining a customer lookup with a refund call that
sets `amount` to the full account balance for a *different* customer's
ID."

**Risk level:** Critical.

**Mappings:** LLM06 (Excessive Agency); CWE-285 (improper
authorization), CWE-639 (authorization bypass through user-controlled
key / IDOR); MITRE ATLAS *LLM Plugin/Tool Abuse*.

**Official link:**
https://genai.owasp.org/resource/owasp-top-10-for-agentic-applications-for-2026/
