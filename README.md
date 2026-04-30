# OWASP Agentic Top 10 — Reference Repository

> Minimal, runnable attack + defense reproducers for the
> [OWASP Top 10 for Agentic Applications (ASI01–ASI10, 2026)](https://owasp.org/www-project-top-10-for-agentic-applications/).
> One folder per category. `docker compose up`, run the exploit, see
> it work, then run the defense and watch it fail.

The repo that should already exist for OWASP ASI the way
[WebGoat](https://owasp.org/www-project-webgoat/) exists for the
classic Top 10 — and now does.

---

## Category matrix

| Code | Category | Attack | Defense | Walkthrough | Status |
|------|----------|--------|---------|-------------|--------|
| ASI01 | Goal Hijacking | [attack](asi01-goal-hijacking/attack/) | [defense](asi01-goal-hijacking/defense/) | [WALKTHROUGH](asi01-goal-hijacking/WALKTHROUGH.md) | v1 ✅ |
| ASI02 | Tool Misuse | [attack](asi02-tool-misuse/attack/) | [defense](asi02-tool-misuse/defense/) | [WALKTHROUGH](asi02-tool-misuse/WALKTHROUGH.md) | v1 ✅ |
| ASI03 | Identity & Authorization Failures | — | — | — | v2 |
| ASI04 | Excessive Agency | — | — | — | v3 |
| ASI05 | Supply Chain & Dependency Attacks | — | — | — | v3 |
| ASI06 | Memory Poisoning | [attack](asi06-memory-poisoning/attack/) | [defense](asi06-memory-poisoning/defense/) | [WALKTHROUGH](asi06-memory-poisoning/WALKTHROUGH.md) | v1 ✅ |
| ASI07 | Insecure Inter-Agent Communication | — | — | — | v2 |
| ASI08 | Cascading Failures | — | — | — | v2 |
| ASI09 | Output Manipulation | — | — | — | v3 |
| ASI10 | Untraceable Behavior | — | — | — | v3 |

---

## Quickstart

Prereqs: Docker, [Ollama](https://ollama.com) running on the host.

```bash
# 1. Pull the model used by the demo agents
ollama pull qwen2.5:3b-instruct

# 2. Pick a category
cd asi02-tool-misuse/attack

# 3. Run the vulnerable agent
docker compose up --build

# 4. In another terminal, watch the attack succeed
docker compose logs -f exfil

# 5. Now run the defense
cd ../defense
docker compose up --build

# 6. Same exploit, blocked
```

Each category folder follows the same structure, so once you've done
one you've done them all.

---

## Repo layout

```
owasp-asi-reference/
├── README.md                       this file
├── CONTRIBUTING.md                 how to add or improve a category
├── LICENSE                         Apache-2.0
├── _shared/                        exfil listener + agent harness
│   ├── exfil_listener/
│   └── agent_harness/
├── asi01-goal-hijacking/
├── asi02-tool-misuse/
├── asi06-memory-poisoning/
└── docs/
    ├── spec.md                     project spec
    ├── lab-setup.md                Docker + Ollama prereqs
    ├── asi-glossary.md             definitions, consistent with OWASP
    └── teaching-with-this-repo.md  for instructors
```

---

## Design principles

1. **One category, one folder, no shared state.** A reader who
   understands ASI02's structure can navigate ASI01 without
   re-learning anything.
2. **Minimal vector per demo.** Single-vector attacks. Chains belong
   in [agentdojo-live](https://github.com/aminrj-labs/agentdojo-live).
3. **Reproducible LLM behaviour.** `temperature=0`, pinned small
   model, attacks aimed at the *tool / memory layer* rather than
   relying on fragile prompt-following.
4. **Read-mostly.** No web UI. No hosted demo. Clone, run, learn.

---

## License

[Apache-2.0](LICENSE).

## Citing

```
@software{owasp_asi_reference_2026,
  title  = {OWASP Agentic Top 10 — Reference Repository},
  author = {Raji, Amine},
  year   = {2026},
  url    = {https://github.com/aminrj-labs/owasp-asi-reference}
}
```

## Related projects

- Upstream OWASP project: [Top 10 for Agentic Applications](https://owasp.org/www-project-top-10-for-agentic-applications/)
- Tool-poisoning origin: [Invariant Labs `mcp-injection-experiments`](https://github.com/invariantlabs-ai/mcp-injection-experiments)
- Adjacent lab: [Appsecco `vulnerable-mcp-servers-lab`](https://github.com/appsecco/vulnerable-mcp-servers-lab)
