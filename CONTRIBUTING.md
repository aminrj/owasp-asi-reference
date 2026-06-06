# Contributing

Thank you for your interest in `owasp-asi-reference`! This document covers
how to contribute new categories, report issues, and submit pull requests.

## Code of Conduct

We follow the [Contributor Covenant Code of Conduct](CODE_OF_CONDUCT.md).
Please read it before contributing.

## Adding a new category

Each category demonstrates one ASI (Agentic Security Issue) from the OWASP
Top 10 for Agentic Applications. To add a new one:

### 1. Choose the ASI ID

Refer to the [OWASP list](https://genai.owasp.org/resource/owasp-top-10-for-agentic-applications-for-2026/)
and pick an ID not yet covered (ASI03, ASI04, ASI05, ASI07, ASI08, ASI09,
ASI10).

### 2. Create the directory structure

```
ASIxx_<slug>/
├── README.md              # Category overview (OWASP rank, explanation, example)
├── attack/
│   ├── Dockerfile
│   ├── docker-compose.yml
│   ├── mcp_server.py      # FastMCP server with vulnerable tools
│   ├── agent.py           # Agent loop (calls LLM + tools)
│   ├── attacker.py        # Driver + canary verdict
│   ├── requirements.txt
│   └── README.md          # Attack explanation + run instructions
└── defense/
    ├── Dockerfile
    ├── docker-compose.yml
    ├── mcp_server.py      # Same tools as attack (defense in agent.py)
    ├── agent.py           # Agent loop with defense hooks
    ├── attacker.py        # Same driver, inverted verdict
    ├── requirements.txt
    ├── <defense_module>.py  # e.g. sanitizer.py, guard.py, policy_enforcer.py
    └── README.md          # Defense explanation + run instructions
```

### 3. Implement the attack

- **`mcp_server.py`**: FastMCP server with 2–3 tools that expose the
  vulnerability. Use `@mcp.tool()` decorators.
- **`agent.py`**: Minimal agent using `shared/agent_loop.py`. System prompt
  should be naive (no defense). Add a `# >>> VULNERABILITY (ASIxx): ... <<<`
  comment.
- **`attacker.py`**: Idempotent driver that:
  1. Resets canary sentinel(s) at start.
  2. Runs `agent.py` via `subprocess`.
  3. Checks canary for the attack signal.
  4. Prints verdict via `shared/console.py.verdict()`.
- **Canary**: Choose a deterministic file path (e.g. `/tmp/xyz.canary` or
  `./data/xyz.canary`). The `attacker.py` checks this file for the expected
  outcome.

### 4. Implement the defense

- **`mcp_server.py`**: Same tools as attack (the defense is in the agent,
  not the tools).
- **`agent.py`**: Same tools but with `on_tool_call` and/or
  `post_tool_result` hooks that enforce the defense. Add a
  `# >>> DEFENSE (ASIxx): ... <<<` comment.
- **`<defense_module>.py`**: Standalone, importable defense logic
  (sanitizer, guard, enforcer, etc.).
- **`attacker.py`**: Same driver, inverted verdict — canary has no violation
  → `ATTACK BLOCKED` (exit 0).

### 5. Docker configuration

- **`Dockerfile`**:
  ```dockerfile
  FROM python:3.12-slim
  WORKDIR /app
  ENV PYTHONUNBUFFERED=1
  COPY requirements.txt .
  RUN pip install --no-cache-dir -r requirements.txt
  COPY shared/ ./shared/
  COPY . .
  ```
- **`docker-compose.yml`**: Two services (`mcp` + `agent`), `agent` depends
  on `mcp` healthy, `extends` from `docker-compose.base.yml` (or define
  `x-llm-env` inline).

### 6. Dependencies

`requirements.txt` must pin exactly:

```
fastmcp==3.3.1
mcp==1.27.0
openai==1.99.0
pydantic==2.11.7
```

Add any category-specific deps (e.g. `PyYAML==6.0.2` for policy enforcement).

### 7. Update top-level files

- Add the new category to the table in `README.md`.
- Add a section to `WALKTHROUGH.md` in the appropriate arc position.
- Update `TODO.md` if tracking remaining categories.

## Submitting changes

1. Create a branch: `git checkout -b category/asiXX_<slug>`
2. Commit with a descriptive message:
   ```
   Add ASI06_X — <description>
   
   - attack/: <brief>
   - defense/: <brief>
   - docs: updated README, WALKTHROUGH
   ```
3. Push and open a pull request.
4. In the PR description, include:
   - Which ASI ID this maps to
   - How to run the attack (expected output)
   - How to run the defense (expected output)
   - Any model requirements (tool-calling support, context window)

## Reporting issues

Use the [issue templates](.github/ISSUE_TEMPLATE/) when filing:

- **Bug report**: Demo doesn't run, verdict is wrong, etc.
- **Feature request**: New category, new defense pattern, etc.
- **Model compatibility**: Specific models that don't work with the demos.

## Style guide

- **Python**: type hints, no bare `except`, f-strings over `.format()`
- **Comments**: `# >>> VULNERABILITY (ASIxx): ... <<<` or
  `# >>> DEFENSE (ASIxx): ... <<<` banners on all Python files
- **Dockerfiles**: `python:3.12-slim`, no CMD (docker-compose controls entry)
- **Docker Compose**: services named exactly `mcp` and `agent`
- **Markdown**: use double-bracket links `[[link]]` only in Obsidian notes;
  use standard `[text](url)` links in project docs

## Questions?

Open an issue or reach out to the maintainer.
