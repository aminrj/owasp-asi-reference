# Teaching with this repo

This repo is designed to be drop-in lab material for an instructor
running a 60–120 minute agentic-security session.

## Session shapes that work

### 90-minute hands-on lab (single category)

| Time | Activity |
|------|----------|
| 00–10 | Slide on the ASI category + threat model |
| 10–20 | Students clone repo, `docker compose up` the `attack/` folder |
| 20–35 | Walk through `WALKTHROUGH.md` together; run `exploit.py` |
| 35–55 | Discussion: where in the agent loop did trust break down? |
| 55–80 | Switch to `defense/`, re-run same exploit, observe block |
| 80–90 | Discussion: what does the canonical defense not cover? |

### Half-day workshop (three categories)

Run the 90-minute shape against ASI01, ASI02, ASI06 back-to-back.
The shared structure means time-to-first-attack drops from ~10 min
in category one to ~2 min by category three.

### CTF-style flag hunt

Each `attack/` folder leaks a flag string to the exfil listener.
Replace the flag with a per-team value (env var override) and score
on time-to-exfil. Then ask teams to submit a defense PR.

## What students should walk away with

- The agent's trust boundary is not "the user"; it's "everything
  the model reads, including tool descriptions and memory."
- Defenses live at the *protocol layer* (MCP), the *prompt layer*,
  and the *retrieval layer* — none of them alone is sufficient.
- Reproducible attack code is more persuasive than slideware.

## Citing in your course materials

```
Amine Raji (2026). "OWASP Agentic Top 10 — Reference Repository."
https://github.com/aminrj-labs/owasp-asi-reference (Apache-2.0)
```

If you adapt the labs into your own course, please open an issue or
PR letting us know — useful signal for the project, and for other
instructors browsing.
