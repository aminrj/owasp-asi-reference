#!/usr/bin/env python3
"""Cross-model evaluation harness for the OWASP ASI reference demos.

Runs every category's attack and defense against a set of local models and
records the three-state verdict for each, then writes a results matrix. The
question it answers is the one the demos are built to answer, at scale:

    which models fall to which attack, and does the defense hold?

Because each demo already resolves to a deterministic, machine-checkable
verdict (SUCCEEDED / BLOCKED / INCONCLUSIVE via canary files and exit codes),
this harness is a thin driver: it sets MODEL_NAME, runs `docker compose up`,
and parses the verdict token the attacker script prints. No new judgement is
introduced here — the repo's own verdict logic is the source of truth.

Usage
-----
    python3 tools/cross_model_eval.py \
        --models qwen2.5:3b-instruct,qwen3:14b,glm-4.7-flash

    python3 tools/cross_model_eval.py --models qwen3:14b --categories ASI01,ASI04

Prerequisites
-------------
Docker + a local OpenAI-compatible endpoint the *containers* can reach. With
Ollama on the host, that means Ollama must listen on 0.0.0.0, not just
localhost, or the containers get "connection refused":

    OLLAMA_HOST=0.0.0.0 ollama serve

The harness runs a preflight check and refuses to start a long matrix if the
endpoint is unreachable, rather than producing a grid of ERRORs.

Stdlib only; no dependencies.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import time
import urllib.request
from dataclasses import dataclass, field
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

# Category directory names, in difficulty order.
CATEGORIES = {
    "ASI01": "ASI01_agent_goal_hijack",
    "ASI02": "ASI02_tool_misuse",
    "ASI04": "ASI04_supply_chain",
    "ASI06": "ASI06_memory_poisoning",
}
PHASES = ("attack", "defense")

# The attacker scripts print exactly one of these, wrapped in ANSI colour.
_VERDICT_RE = re.compile(r"\[(SUCCEEDED|BLOCKED|FAILED|INCONCLUSIVE)\]")

# How each verdict reads per phase, for the results matrix.
_GLYPH = {
    ("attack", "SUCCEEDED"): "SUCCEEDED",       # model was exploited
    ("attack", "INCONCLUSIVE"): "declined",     # model refused on its own
    ("attack", "FAILED"): "failed",             # fired but missed the sink
    ("defense", "BLOCKED"): "BLOCKED",          # control held
    ("defense", "SUCCEEDED"): "DEFENSE-FAILED", # control bypassed
    ("defense", "INCONCLUSIVE"): "declined",
    ("defense", "FAILED"): "failed",
}


@dataclass
class RunResult:
    model: str
    category: str
    phase: str
    verdict: str          # SUCCEEDED | BLOCKED | FAILED | INCONCLUSIVE | ERROR | TIMEOUT
    seconds: float
    detail: str = ""


@dataclass
class Matrix:
    results: list[RunResult] = field(default_factory=list)

    def cell(self, model: str, category: str, phase: str) -> str:
        for r in self.results:
            if r.model == model and r.category == category and r.phase == phase:
                return _GLYPH.get((phase, r.verdict), r.verdict)
        return "-"


# --------------------------------------------------------------------------


def preflight(base_url: str) -> bool:
    """Confirm the model endpoint answers before committing to a long matrix."""
    tags = base_url.rstrip("/").replace("/v1", "") + "/api/tags"
    try:
        with urllib.request.urlopen(tags, timeout=6) as resp:
            models = [m["name"] for m in json.load(resp).get("models", [])]
        print(f"  endpoint OK — {len(models)} models available")
        return True
    except Exception as exc:  # noqa: BLE001
        print(f"  endpoint check failed at {tags}: {exc}")
        print("  if Ollama is on the host, start it with OLLAMA_HOST=0.0.0.0 so")
        print("  the demo containers can reach it (host.docker.internal).")
        return False


def run_one(model: str, category: str, phase: str, timeout: int) -> RunResult:
    workdir = REPO_ROOT / CATEGORIES[category] / phase
    # Clear canaries so a stale file from a prior run can't be misread.
    for canary in (workdir / "data").glob("*.canary"):
        canary.unlink()

    started = time.monotonic()
    try:
        proc = subprocess.run(
            ["docker", "compose", "up", "--build", "--abort-on-container-exit"],
            cwd=workdir,
            env={**_base_env(), "MODEL_NAME": model},
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        out = proc.stdout + proc.stderr
        verdict = _extract_verdict(out)
        detail = "" if verdict != "ERROR" else _first_error(out)
    except subprocess.TimeoutExpired:
        verdict, detail = "TIMEOUT", f"exceeded {timeout}s"
    finally:
        subprocess.run(
            ["docker", "compose", "down", "--remove-orphans"],
            cwd=workdir, capture_output=True, text=True,
        )
    return RunResult(model, category, phase, verdict, time.monotonic() - started, detail)


def _extract_verdict(output: str) -> str:
    hits = _VERDICT_RE.findall(output)
    return hits[-1] if hits else "ERROR"


def _first_error(output: str) -> str:
    for line in output.splitlines():
        if any(k in line for k in ("Error", "error:", "Traceback", "refused", "no such")):
            return line.strip()[:160]
    return "no verdict token in output"


def _base_env() -> dict:
    import os
    return dict(os.environ)


# --------------------------------------------------------------------------


def render_markdown(matrix: Matrix, models: list[str], categories: list[str]) -> str:
    lines = ["# Cross-model evaluation", ""]
    lines.append("Attack verdict / defense verdict per category, per model. "
                 "`SUCCEEDED` in the attack column means the model was exploited; "
                 "`BLOCKED` in the defense column means the control held; "
                 "`declined` means the model refused on its own (not proof of safety).")
    lines.append("")
    header = "| Category | " + " | ".join(models) + " |"
    sep = "|" + "---|" * (len(models) + 1)
    lines += [header, sep]
    for cat in categories:
        cells = []
        for m in models:
            a = matrix.cell(m, cat, "attack")
            d = matrix.cell(m, cat, "defense")
            cells.append(f"{a} / {d}")
        lines.append(f"| {cat} | " + " | ".join(cells) + " |")
    lines.append("")
    # Per-model summary.
    lines += ["## Summary", ""]
    for m in models:
        exploited = sum(
            1 for c in categories if matrix.cell(m, c, "attack") == "SUCCEEDED"
        )
        held = sum(1 for c in categories if matrix.cell(m, c, "defense") == "BLOCKED")
        lines.append(f"- **{m}** — exploited by {exploited}/{len(categories)} attacks; "
                     f"defense held on {held}/{len(categories)}.")
    return "\n".join(lines) + "\n"


def main() -> int:
    ap = argparse.ArgumentParser(description="Cross-model eval for the ASI demos")
    ap.add_argument("--models", required=True,
                    help="comma-separated model names (as Ollama lists them)")
    ap.add_argument("--categories", default=",".join(CATEGORIES),
                    help="comma-separated subset of ASI01,ASI02,ASI04,ASI06")
    ap.add_argument("--phases", default=",".join(PHASES),
                    help="comma-separated subset of attack,defense")
    ap.add_argument("--timeout", type=int, default=240, help="per-run timeout (s)")
    ap.add_argument("--base-url", default="http://localhost:11434/v1",
                    help="endpoint for the preflight check (host side)")
    ap.add_argument("--out", default=str(REPO_ROOT / "tools" / "eval_results.md"))
    ap.add_argument("--skip-preflight", action="store_true")
    args = ap.parse_args()

    models = [m.strip() for m in args.models.split(",") if m.strip()]
    categories = [c.strip() for c in args.categories.split(",") if c.strip()]
    phases = [p.strip() for p in args.phases.split(",") if p.strip()]

    print(f"Cross-model eval: {len(models)} models x {len(categories)} categories "
          f"x {len(phases)} phases = {len(models)*len(categories)*len(phases)} runs")
    if not args.skip_preflight and not preflight(args.base_url):
        return 2

    matrix = Matrix()
    total = len(models) * len(categories) * len(phases)
    n = 0
    for model in models:
        for cat in categories:
            for phase in phases:
                n += 1
                print(f"[{n}/{total}] {model} · {cat} · {phase} ... ", end="", flush=True)
                res = run_one(model, cat, phase, args.timeout)
                matrix.results.append(res)
                tag = _GLYPH.get((phase, res.verdict), res.verdict)
                print(f"{tag} ({res.seconds:.0f}s)"
                      + (f" — {res.detail}" if res.detail else ""))

    md = render_markdown(matrix, models, categories)
    Path(args.out).write_text(md)
    json_out = Path(args.out).with_suffix(".json")
    json_out.write_text(json.dumps([r.__dict__ for r in matrix.results], indent=2))
    print(f"\nWrote {args.out} and {json_out.name}")
    print("\n" + md)
    return 0


if __name__ == "__main__":
    sys.exit(main())
