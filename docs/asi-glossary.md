# ASI Glossary

Definitions track the [OWASP Top 10 for Agentic Applications](https://owasp.org/www-project-top-10-for-agentic-applications/).
Wording is paraphrased; canonical text lives upstream.

| Code | Name | One-line definition |
|------|------|---------------------|
| ASI01 | Goal Hijacking | The agent is steered into pursuing an attacker-chosen objective via injected instructions in tool output, retrieved content, or user input. |
| ASI02 | Tool Misuse | A tool the agent has access to is malicious, has been rug-pulled, or is invoked in an unsafe way the agent doesn't recognize. |
| ASI03 | Identity & Authorization Failures | The agent acts with the wrong identity, broader scopes than intended, or impersonates a user across boundaries. |
| ASI04 | Excessive Agency | The agent has more permissions, autonomy, or side-effect surface area than its task requires. |
| ASI05 | Supply Chain & Dependency Attacks | A model, tool, prompt template, or library the agent depends on has been tampered with upstream. |
| ASI06 | Memory Poisoning | Attacker-controlled content is written into long-term memory and then trusted on retrieval. |
| ASI07 | Insecure Inter-Agent Communication | Multi-agent systems trust messages between agents without authentication, integrity, or scope checks. |
| ASI08 | Cascading Failures | A failure or compromise in one agent / tool / step propagates uncontrollably through the system. |
| ASI09 | Output Manipulation | Agent output (rendered HTML, generated code, executed shell) is treated as trusted by a downstream consumer. |
| ASI10 | Untraceable Behavior | Insufficient logging or attribution makes it impossible to reconstruct what an agent did and why. |
