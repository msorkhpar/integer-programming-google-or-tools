"""Why a request has no plan, and why a project was left out. Stub: lesson 14.2.6 writes it."""

from __future__ import annotations

from dataclasses import dataclass

from .data import Request


@dataclass(frozen=True)
class Conflict:
    rows: list[str]
    message: str


@dataclass(frozen=True)
class Deferral:
    project: str
    npv_cost: float
    displaced: tuple[str, ...]
    conflict: Conflict | None


def why_infeasible(request: Request) -> Conflict | None:
    """The rows that clash. Stub: reports none."""
    return None


def why_deferred(request: Request, plan, project_id: str) -> Deferral:
    """What funding `project_id` would cost. Stub: nothing."""
    return Deferral(project_id, 0.0, (), None)


def deletion_filter(built: Built, keep: tuple[str, ...] = ()) -> list[str]:
    """Returns, sorted, the names of an irreducible set of rows that cannot all hold: relax each row in name order, keep it relaxed while the model stays infeasible, restore it when relaxing it makes the model feasible. Rows named in keep are never relaxed."""
    return []


def feasible(built: Built) -> bool:
    """True unless HiGHS reports the model infeasible: only the termination INFEASIBLE counts as no plan, and INFEASIBLE_OR_UNBOUNDED counts as feasible (every variable is binary, so the model is never unbounded)."""
    return True


def describe(request: Request, name: str) -> str:
    """Returns one row in the planners' words, read from its name: `spend in <y> within $<b>k`, `<id> is a must-do`, `<id> is forced in`, `at most one of <ids>` (the group's members in id order, joined by a comma and a space), `<a> and <b> are funded together or not at all`, `<child> started by <t> needs <parent> started by <t - lag>`, `remove at least $<floor>k of risk` (one decimal, thousands commas) for the risk floor; the name itself for any other row. The kind is the part of the name before its first underscore."""
    return name


def explain(request: Request, rows: list[str]) -> Conflict:
    """Returns a Conflict with the rows and a message: `No plan meets these <n> rules together; drop or change any one of them:` then one line `  <row>: <description>` per row."""
    return Conflict(rows, "")
