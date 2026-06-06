"""Colored PASS/FAIL/SUCCEEDED/BLOCKED printing.

All six ``attacker.py`` scripts use these helpers so output is
consistent across categories.
"""
from __future__ import annotations

import sys

# ANSI colour codes
_GREEN = "\033[92m"
_RED = "\033[91m"
_DIM = "\033[2m"
_RESET = "\033[0m"


def succeeded(msg: str) -> None:
    """Print a green SUCCEEDED message."""
    print(f"{_GREEN}[SUCCEEDED]{_RESET} {msg}", file=sys.stdout, flush=True)


def blocked(msg: str) -> None:
    """Print a green BLOCKED message (defense held)."""
    print(f"{_GREEN}[BLOCKED]{_RESET} {msg}", file=sys.stdout, flush=True)


def failed(msg: str) -> None:
    """Print a red FAILED message."""
    print(f"{_RED}[FAILED]{_RESET} {msg}", file=sys.stdout, flush=True)


def info(msg: str) -> None:
    """Print a dim informational message."""
    print(f"{_DIM}[info]{_RESET} {msg}", file=sys.stderr, flush=True)


def verdict(attack_succeeded: bool, in_defense: bool) -> int:
    """Centralize the SUCCEEDED/BLOCKED/FAILED + exit-code logic.

    Parameters
    ----------
    attack_succeeded : bool
        Whether the attack signal was observed (canary match, exfil, etc.).
    in_defense : bool
        Whether we are running in a defense folder.

    Returns
    -------
    int
        0 if the expected outcome occurred, non-zero otherwise.

    Exit-code rules (SPEC §5.5)
    ---------------------------
    * attack folder + attack succeeded → SUCCEEDED, exit 0
    * defense folder + attack blocked (not succeeded) → BLOCKED, exit 0
    * defense folder + attack succeeded → DEFENSE FAILED, exit 1
    * attack folder + attack not succeeded → ATTACK FAILED, exit 1
    """
    if in_defense:
        if not attack_succeeded:
            blocked("Attack blocked — defense held.")
            return 0
        else:
            failed("Defense failed — attack succeeded despite controls.")
            return 1
    else:
        if attack_succeeded:
            succeeded("Attack succeeded.")
            return 0
        else:
            failed("Attack failed — unexpected in attack folder.")
            return 1
