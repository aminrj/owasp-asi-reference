# Security Policy

## Scope

This repository contains **intentionally vulnerable code** for educational
and research purposes. The vulnerabilities demonstrated are real and
applicable to production agentic systems.

**This code must never be deployed in production.**

## What this repo is

- **Learning tool** — runnable attack→defense demos for the OWASP Top 10
  for Agentic Applications.
- **Research platform** — minimal, reproducible attack patterns for testing
  defensive controls.
- **Reference implementation** — shows how specific ASI vulnerabilities
  manifest and how they can be mitigated.

## What this repo is NOT

- A production security framework.
- A scanner or automated testing tool.
- A replacement for proper application security practices.

## Reporting a vulnerability

If you discover a vulnerability in this repository's code itself
(e.g., a demo that causes unintended system access beyond its intended
scope, a dependency with a known CVE, or a security issue in the
documentation), please report it to:

**amine [at] aminrj-labs [dot] com**

We aim to acknowledge reports within 48 hours and provide updates
as remediation progresses.

### What to include

- Description of the vulnerability
- Steps to reproduce
- Impact assessment (if known)
- Suggested fix (optional)

### What to expect

- Acknowledgment within 48 hours
- Timeline for remediation (typically 2–4 weeks for non-critical,
  immediate for critical issues)
- Credit in the changelog (optional)

## Known risks

| Risk | Mitigation |
|------|------------|
| Demos run code that sends messages to attacker-controlled addresses | All communication is local (canary files, no network exfil) |
| Models may produce unexpected outputs | Verdicts are deterministic (canary-based), not LLM-dependent |
| Docker containers run with standard user permissions | No privileged containers, no host filesystem access |
| Dependencies may have vulnerabilities | Pinned versions, reviewed at release time |

## Dependencies

This repo pins all Python dependencies to exact versions. Dependencies are:

- `fastmcp==3.3.1` — MCP server framework
- `mcp==1.27.0` — MCP client SDK
- `openai==1.99.0` — OpenAI-compatible API client
- `pydantic==2.11.7` — Data validation
- `PyYAML==6.0.2` — Policy file parsing (ASI02 defense only)

We monitor these for CVEs and update at each release.

## Disclosure policy

We follow a 90-day disclosure window. Critical vulnerabilities will be
patched immediately with a new release.
