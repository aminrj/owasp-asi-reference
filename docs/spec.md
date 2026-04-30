# 05 — owasp-asi-reference

> Ten folders, one per OWASP Agentic Top 10 category (ASI01–ASI10). Each contains a minimal docker-compose reproducer of the canonical attack and a working defense, with a short README mapping to the OWASP entry. The "show me a working ASI03 attack" repo that doesn't exist yet — destined to be cited from other people's blog posts and conference talks.

---

## 1. Why this exists

**The gap.** OWASP Top 10 for Agentic Applications 2026 is published, well-circulated, and influential. But there is no canonical companion repo of *minimal reproducible attacks and defenses* for each ASI category. Your Week 1 lab covers ASI01–ASI06 in depth, your Week 2 spec covers all ten — but they live inside paid course materials. WebGoat, Juice Shop, and DVWA exist for traditional appsec; the agentic equivalent is missing.

This is also the lowest-effort project on your list, because most of the content already exists in your Week 1 / Week 2 work. You're extracting and refactoring, not creating from scratch.

**Why you, why now.** OWASP visibility is one of your stated long-term goals (Steve Wilson, OWASP Agentic Security project). The way that visibility actually accrues isn't through proposing big contributions — it's through being the person whose repo is linked from the OWASP project page as the canonical reference. This repo is the lowest-friction path to that link.

**What it changes.** Your name attaches to the OWASP Agentic Top 10 the way "WebGoat" attaches to OWASP Top 10. Every blog post, every talk, every training course about agentic AI security has a footnote linking to your reference repo. That footnote compounds — every citation drives a star, every star reinforces credibility, every credibility tick lowers the friction on speaking invitations.

---

## 2. What you are building (v1 scope)

A public GitHub repo at `aminrj-labs/owasp-asi-reference` containing:

- **Three folders at v1**: ASI01, ASI02, ASI06 (your three strongest categories from existing Week 1 / Week 2 work)
- **Each folder contains**:
  - `README.md` — what the category is, two paragraph summary, link to OWASP entry
  - `attack/` — minimal docker-compose with vulnerable agent + exploit script
  - `defense/` — same setup with the canonical control applied
  - `WALKTHROUGH.md` — narrative explanation: setup → attack → observation → defense → re-test
- **A top-level README** that orients readers and links to OWASP project resources
- **A consistent docker-compose pattern** so a reader who learns ASI01's structure can navigate ASI02 without re-learning

### Explicitly out of scope for v1
- All 10 categories (start with 3, expand iteratively)
- Sophisticated attack chains (single-vector demonstrations only — chains belong in agentdojo-live missions)
- A web UI / hosted demos (nothing deployed; readers run locally)
- Comprehensive enterprise-grade defenses (canonical control, not production-ready library)
- Non-MCP-based agent frameworks at v1 (LangChain/LangGraph/AutoGen demos can come in v2)

### What "done" looks like for v1
- Three category folders with attack + defense + walkthrough
- Top-level README that's pleasant to read and orients newcomers
- Each docker-compose works end-to-end with `docker compose up` + a single command
- Linked from at least one of: aminrj.com speaker page, course landing page, your newsletter
- Public; the OWASP Agentic Security project lead (Steve Wilson) has been notified

---

## 3. How a reader works with it

### The 90-second navigation flow

```
reader.lands on README
  → sees the matrix:
    ASI01 Goal Hijacking          [attack] [defense] [walkthrough]
    ASI02 Tool Misuse             [attack] [defense] [walkthrough]
    ASI06 Memory Poisoning        [attack] [defense] [walkthrough]
    ASI03 Authz Failures          (coming in v2)
    ...

  → clicks ASI02
  → reads 2-paragraph summary
  → cd asi02/attack
  → docker compose up
  → in another terminal: python exploit.py
  → sees the attack succeed (file exfil to local listener)
  → reads WALKTHROUGH.md to understand why
  → cd ../defense
  → docker compose up (with control applied)
  → re-runs exploit
  → sees defense block it
```

The whole flow takes 90 seconds for a competent practitioner. That's what makes it the kind of repo people link to — minimal friction, immediate insight.

### Each category folder is self-contained

```
asi02/
├── README.md                    overview
├── WALKTHROUGH.md               narrative (the teaching part)
├── attack/
│   ├── docker-compose.yml
│   ├── malicious_mcp_server.py
│   ├── exploit.py
│   └── expected_output.txt
└── defense/
    ├── docker-compose.yml
    ├── malicious_mcp_server.py    same attack
    ├── defense_proxy.py            mcp-canary or similar
    ├── exploit.py
    └── expected_output.txt          shows defense blocking
```

This is essentially a refactor + extraction of work you've already done in Week 1 / Week 2. The hard part isn't building it — it's deciding *not* to gold-plate it.

---

## 4. Inspiration / baseline

| Project | What to learn from | What to do differently |
|---|---|---|
| **OWASP WebGoat** | Decade-spanning canonical reference repo for the original OWASP Top 10. Every appsec engineer knows it. | Same model, agentic AI domain. Yours is read-mostly (no UI to set up) where WebGoat is interactive — you're closer to a "minimum viable WebGoat." |
| **OWASP Juice Shop** | Vulnerable-by-design, fun to attack, used in CTFs everywhere. | Juice Shop is one big vulnerable app. Yours is ten small ones. Different shape, same DNA. |
| **DVWA / DVNA / WebGoat-like things** | The "minimal vulnerable thing per category" pattern. | Reapply to agent security. |
| **Atomic Red Team** | Per-technique reproducible folder structure, mapped to a public framework (MITRE ATT&CK). | Yours is mapped to OWASP ASI codes. Same ergonomics. |
| **CloudGoat** (Rhino Security Labs) | Per-scenario AWS attack labs with terraform + walkthrough. | You're using docker-compose instead of terraform, agentic-AI instead of cloud. |
| **Appsecco vulnerable-mcp-servers-lab** | Adjacent — vulnerable MCP servers for hands-on training. | Theirs is a flat list of vulnerable servers. Yours is structured around OWASP ASI codes — a different navigation model that maps to the spec. |
| **mcp-injection-experiments** (Invariant Labs) | The original attack scripts for tool poisoning and rug-pull. | Cite as upstream source for ASI02 examples. Your repo organizes the universe; theirs is one corner of it. |

Combined inspiration: **WebGoat's canonical-repo legacy + Atomic Red Team's per-technique structure + the Appsecco lab's MCP-specific attack content.**

---

## 5. Architecture

There is essentially no architecture. Each category folder is independent docker-compose. That's intentional — readers don't have to understand a system to use one folder.

```
owasp-asi-reference/
│
│   no shared infrastructure
│   no global state
│   no orchestration
│
├── asi01/        independent
├── asi02/        independent
├── asi03/        (v2)
├── ...
└── README.md     map / index
```

The only shared component is a `_shared/` folder with:
- A common exfil listener (Flask, port 8888, prints stolen data)
- A common Ollama-config helper for the agent containers
- A common Python base for the agent harness (refactored from your Week 1 lab)

```
_shared/
├── exfil_listener/
│   ├── app.py
│   └── docker-compose.yml
├── agent_harness/
│   ├── harness.py
│   └── README.md
└── README.md
```

Each ASI folder's docker-compose references `_shared` via volume mount or via a `docker-compose.shared.yml` overlay. Readers don't need to think about it; they just `docker compose up`.

---

## 6. Repo structure

```
owasp-asi-reference/
├── README.md                       category matrix + how to use
├── CONTRIBUTING.md                 how to add a category or improve one
├── LICENSE                         Apache-2
│
├── _shared/
│   ├── exfil_listener/
│   ├── agent_harness/
│   └── README.md
│
├── asi01-goal-hijacking/
│   ├── README.md
│   ├── WALKTHROUGH.md
│   ├── attack/
│   └── defense/
│
├── asi02-tool-misuse/
│   ├── README.md
│   ├── WALKTHROUGH.md
│   ├── attack/
│   └── defense/
│
├── asi06-memory-poisoning/
│   ├── README.md
│   ├── WALKTHROUGH.md
│   ├── attack/
│   └── defense/
│
└── docs/
    ├── asi-glossary.md             definitions consistent with OWASP
    ├── lab-setup.md                prereqs (Docker, Ollama)
    └── teaching-with-this-repo.md  for instructors who use it in training
```

---

## 7. Deployment

**No, this does not deploy as a service.** It's a reference repo. Readers clone it and run things locally on their own machine.

The only "deployment" is the GitHub repo itself being public and the GitHub Pages site rendering the README + walkthroughs nicely.

### Optional: GitHub Pages
- Render walkthroughs as static HTML pages with consistent styling
- Add a top navigation by category
- Free, zero-ops

---

## 8. Roadmap

**v1 (target: 2 weekends, June 2026 — after agentdojo-live and mcp-canary are launched)**
- ASI01, ASI02, ASI06 fully covered
- _shared/ scaffolding works
- Top-level README with the category matrix
- GitHub Pages rendering walkthroughs

**v2 (target: end of Aug 2026)**
- ASI03 (Identity & Authz Failures) — extract from Week 2 Mission 03
- ASI07 (Insecure Inter-Agent Comm) — extract from Week 2 Mission 04
- ASI08 (Cascading Failures) — extract from Week 2 Mission 05
- Notify Steve Wilson and OWASP Agentic Security project
- Propose linking from the official OWASP project page

**v3 (target: Q4 2026)**
- ASI04, ASI05, ASI09, ASI10 — complete the matrix
- Add LangChain/LangGraph/AutoGen variants for at least 3 categories (broader audience)
- Translation: Spanish + Mandarin (community PRs welcome)
- Optional: GitHub Codespaces config so readers don't need local Docker

---

## 9. Anti-drift checklist

### Definition of done for v1
- [ ] Three category folders complete: attack works, defense works, walkthrough is readable
- [ ] _shared/ scaffolding tested across all three categories
- [ ] Top-level README has the category matrix and quickstart
- [ ] GitHub Pages site renders cleanly
- [ ] Steve Wilson (OWASP) has received a polite notification with the repo URL

### Forbidden in v1 (resist the temptation)
- Trying to ship all 10 categories at v1 (you'll never finish — start with 3)
- Adding LangChain/LangGraph/AutoGen variants before the MCP versions are clean
- Building an interactive UI on top of the repo
- Writing a 30-page whitepaper (the walkthroughs are enough)
- Translation work before English content stabilizes

### Drift signals
- You've spent more than 2 weekends on this and have fewer than 3 categories complete
- You're refactoring _shared/ a third time
- You're tweaking the README's category matrix layout instead of writing walkthroughs
- You've started a side-quest into "let me also rewrite the OWASP descriptions in clearer language"
- More than 7 days have passed without a commit

### A note specific to this repo
This is the easiest of your 5 projects in absolute terms but the easiest to *not finish* because there's no urgency. Set a hard deadline (end of June 2026) and treat shipping v1 as non-negotiable. The compounding citation effect only starts after public launch.

---

## 10. Distribution & launch

### Distribution shape
This is the project least likely to "go viral" on launch — and that's correct. Reference repos don't trend on HN; they accrue stars slowly through citations from other content. Your distribution strategy is therefore different from agentdojo-live or mcp-bench:

- **Cite this repo from your other projects' READMEs.** agentdojo-live's solution writeups link to the corresponding ASI walkthrough. mcp-bench's methodology page references the canonical attack definitions here.
- **Cite from your own blog posts and newsletter issues.** Every time you write about ASI02, link the asi02/ folder.
- **Cite from your speaker page.** "Background reading for the talks" section.
- **Light external push at v1**:
  - Newsletter issue introducing it
  - A short LinkedIn post (link in first comment)
  - Direct DM to Steve Wilson (OWASP) and a couple of tl;dr sec / Adversa AI roundup curators
- **Don't HN-launch it.** It's not the right shape. Save HN energy for agentdojo-live, mcp-canary, and mcp-bench.

### What success looks like, 6 months post-launch
- 200+ GitHub stars (slower growth than your other projects, that's fine)
- Linked from the official OWASP Agentic Security project page
- Cited in at least 5 external blog posts or talks
- Used as a teaching reference by at least 2 other course creators or trainers (you may not even know about this — count it from PRs and issues)
- Becomes the example you point to when explaining what ASI02 looks like in practice
