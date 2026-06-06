"""ASI02 defense — runtime policy enforcement.

Importable:
    from policy_enforcer import enforce, PolicyViolation

A runtime reference monitor that wraps every tool call:
  1. Loads policy.yaml (pydantic-validated schema).
  2. ``enforce(tool_name, params, session)`` — denies disallowed tools;
     evaluates each declared constraint against the actual params +
     session; raises ``PolicyViolation`` on breach.
  3. Constraint mini-evaluator supports ``==``, ``<=``, ``>=``, ``in``
     against ``session.*`` and literals. Keep it tiny and safe (no
     ``eval``).
"""
from __future__ import annotations

import os
import re
from dataclasses import dataclass

import yaml
from pydantic import BaseModel, Field


class ToolConstraint(BaseModel):
    tool_name: str
    allow: bool
    constraints: dict[str, str] = Field(default_factory=dict)


class PolicySchema(BaseModel):
    session: dict[str, str]
    tools: dict[str, ToolConstraint]


@dataclass
class PolicyViolation:
    tool_name: str
    param: str
    constraint: str
    actual_value: str
    reason: str


class PolicyEnforcer:
    """Loads policy.yaml and enforces every tool call against it."""

    def __init__(self, policy_path: str = "policy.yaml"):
        with open(policy_path, "r") as f:
            raw = yaml.safe_load(f)
        self.policy = PolicySchema(**raw)
        self.session: dict[str, str] = {}
        for key, env_var in self.policy.session.items():
            self.session[key] = os.environ.get(env_var, "")

    def enforce(self, tool_name: str, params: dict) -> None:
        """Enforce the policy for a tool call.

        # >>> DEFENSE (ASI02): authority enforced at the tool boundary,
        # independent of model/prompt; least-agency by allowlist <<<

        Raises ``PolicyViolation`` on breach (logged, surfaced, refused).
        """
        tool_policy = self.policy.tools.get(tool_name)
        if tool_policy is None:
            raise PolicyViolation(
                tool_name=tool_name,
                param="",
                constraint="",
                actual_value="",
                reason=f"tool {tool_name!r} is not defined in policy",
            )

        if not tool_policy.allow:
            raise PolicyViolation(
                tool_name=tool_name,
                param="",
                constraint="",
                actual_value="",
                reason=f"tool {tool_name!r} is disallowed by policy",
            )

        for param_name, constraint_expr in tool_policy.constraints.items():
            actual = params.get(param_name)
            if actual is None:
                continue
            violation = self._evaluate_constraint(
                param_name, constraint_expr, actual
            )
            if violation is not None:
                raise violation

    def _evaluate_constraint(
        self, param_name: str, expr: str, actual: object
    ) -> PolicyViolation | None:
        """Evaluate a single constraint expression.

        Supports:
          - ``== session.<key>`` — must equal a session value
          - ``== <literal>`` — must equal a literal
          - ``<= <number>`` — must be <= a number
          - ``>= <number>`` — must be >= a number
          - ``in <list>`` — must be in a comma-separated list
        """
        expr = expr.strip()

        # session reference: == session.customer_id
        session_match = re.match(r"==\s*session\.(\w+)", expr)
        if session_match:
            session_key = session_match.group(1)
            session_val = self.session.get(session_key, "")
            if str(actual) != str(session_val):
                return PolicyViolation(
                    tool_name="",
                    param=param_name,
                    constraint=expr,
                    actual_value=str(actual),
                    reason=f"{param_name} {actual!r} != session.{session_key} {session_val!r}",
                )
            return None

        # comparison: <= 50, >= 0
        comp_match = re.match(r"(<=|>=)\s*([\d.]+)", expr)
        if comp_match:
            op, limit_str = comp_match.groups()
            limit = float(limit_str)
            actual_num = float(actual)
            if op == "<=" and actual_num > limit:
                return PolicyViolation(
                    tool_name="",
                    param=param_name,
                    constraint=expr,
                    actual_value=str(actual),
                    reason=f"{param_name} {actual_num} > {limit}",
                )
            if op == ">=" and actual_num < limit:
                return PolicyViolation(
                    tool_name="",
                    param=param_name,
                    constraint=expr,
                    actual_value=str(actual),
                    reason=f"{param_name} {actual_num} < {limit}",
                )
            return None

        return None


# Module-level singleton — loaded once at agent startup.
_enforcer: PolicyEnforcer | None = None


def get_enforcer() -> PolicyEnforcer:
    global _enforcer
    if _enforcer is None:
        _enforcer = PolicyEnforcer()
    return _enforcer


def enforce(tool_name: str, params: dict) -> None:
    """Convenience function: enforce against the loaded policy."""
    get_enforcer().enforce(tool_name, params)
