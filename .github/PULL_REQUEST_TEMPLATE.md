## Description

A clear and concise description of what this PR changes.

## Type of change

- [ ] New category (ASI0X)
- [ ] New defense pattern
- [ ] Bug fix
- [ ] Documentation update
- [ ] Dependency update
- [ ] Architecture change
- [ ] Other (please describe)

## Category details (if applicable)

- **ASI ID**: (e.g. ASI03)
- **Channel**: (input / state / action)
- **Attack**: (brief description)
- **Defense**: (brief description)

## How to test

### Attack

```bash
cd ASI0X_<slug>/attack
docker compose up --abort-on-container-exit
```

**Expected output:**
```
[SUCCEEDED] Attack succeeded.
```

### Defense

```bash
cd ASI0X_<slug>/defense
docker compose up --abort-on-container-exit
```

**Expected output:**
```
[BLOCKED] Attack blocked — defense held.
```

## Model requirements

- [ ] Works with any tool-calling model
- [ ] Requires specific model: (e.g. `qwen2.5:7b-instruct`)
- [ ] Other: (describe)

## Checklist

- [ ] I have read the [CONTRIBUTING.md](CONTRIBUTING.md) guide.
- [ ] All Python files have `# >>> VULNERABILITY (ASIxx): ... <<<` or
      `# >>> DEFENSE (ASIxx): ... <<<` banners.
- [ ] Dockerfiles use `python:3.12-slim`.
- [ ] `requirements.txt` pins exact dependency versions.
- [ ] `docker-compose.yml` has services named exactly `mcp` and `agent`.
- [ ] `attacker.py` is idempotent (resets canary at start).
- [ ] I have updated `README.md` (category table) if applicable.
- [ ] I have updated `WALKTHROUGH.md` if applicable.

## Related issues

Fixes #(issue number)
