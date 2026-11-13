"""Scenarios: what planners change before a run, kept as data beside the export they change.

A scenario never edits the export. It names budget changes and overrides, and `apply` turns them
into a new Request; the overrides become named rows (rules.overrides), so the diagnostics of lesson
14.2.6 can name an override that clashes with a rule. `diff` compares two plans (lesson 9.3.3).
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field, replace

from .data import Request
from .plan import Plan


@dataclass(frozen=True)
class Scenario:
    name: str
    budget: dict[int, int] = field(default_factory=dict)      # year -> $k, replaces that year's budget
    force_in: tuple[str, ...] = ()
    force_out: tuple[str, ...] = ()
    fix_start: dict[str, int] = field(default_factory=dict)   # project -> the year it must start
    note: str = ""                                            # why: the audit trail's one line

    def to_dict(self) -> dict:
        data = asdict(self)
        data["budget"] = {str(y): v for y, v in self.budget.items()}
        return {**data, "force_in": list(self.force_in), "force_out": list(self.force_out)}

    @classmethod
    def from_dict(cls, data: dict) -> "Scenario":
        return cls(name=data["name"], budget={int(y): v for y, v in data["budget"].items()},
                   force_in=tuple(data["force_in"]), force_out=tuple(data["force_out"]),
                   fix_start=dict(data["fix_start"]), note=data["note"])


def apply(request: Request, scenario: Scenario) -> Request:
    """The request with the scenario's budgets and overrides; refuses projects the export lacks."""
    named = set(scenario.force_in) | set(scenario.force_out) | set(scenario.fix_start)
    unknown = sorted(named - {p.project_id for p in request.projects})
    if unknown:
        raise ValueError(f"scenario {scenario.name} names unknown projects: {', '.join(unknown)}")
    return replace(request, name=f"{request.name} / {scenario.name}",
                   budget={**request.budget, **scenario.budget},
                   force_in=scenario.force_in, force_out=scenario.force_out, fix_start=dict(scenario.fix_start))


@dataclass(frozen=True)
class Diff:
    selected: tuple[str, ...]                   # funded in the other plan only
    deferred: tuple[str, ...]                   # funded in the base plan only
    shifted: tuple[tuple[str, int, int], ...]   # (project, base start, other start)


def diff(base: Plan, other: Plan) -> Diff:
    return Diff(
        selected=tuple(p for p in other.funded if p not in base.starts),
        deferred=tuple(p for p in base.funded if p not in other.starts),
        shifted=tuple((p, base.starts[p], other.starts[p]) for p in base.funded
                      if p in other.starts and other.starts[p] != base.starts[p]),
    )
