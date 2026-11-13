"""Scenarios as data: create, copy, optimize (lesson 12.1.1), with overrides (12.1.2).

A `Scenario` is plain data. It names the portfolio it plans (by size, seed and content hash), the
budgets, the overrides in force and the solver settings, plus who created it, when, and which
scenario it was copied from. The model is never stored: `optimize` builds it from the scenario
every time, so the same scenario always gives the same model.

GridCap is a fictional utility's portfolio, generated for this course; no number in it is real.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field

from ortools.math_opt.python import mathopt

from gridcap import Portfolio, generate
from overrides import Override, bounds_of
from plan_model import build, solve_highs

#: The solver settings a scenario starts with (section 10 explains each one).
SETTINGS = {"solver": "HIGHS", "relative_gap_tolerance": 0.0}


@dataclass(frozen=True)
class DataRef:
    """Which portfolio a scenario plans: enough to regenerate it, and its hash to prove it is the same."""

    size: str
    seed: int
    content_hash: str


@dataclass
class Scenario:
    scenario_id: str
    name: str
    data: DataRef
    budget: dict[int, int]
    settings: dict
    overrides: dict[str, Override] = field(default_factory=dict)   # project -> the override in force
    parent_id: str | None = None
    created_by: str = ""
    created_at: str = ""

    def inputs(self) -> dict:
        """Everything the model is built from, and nothing else, in a JSON-ready form."""
        return {"data": {"size": self.data.size, "seed": self.data.seed, "hash": self.data.content_hash},
                "budget": {str(y): v for y, v in sorted(self.budget.items())},
                "overrides": [[o.project, o.kind, o.year] for _, o in sorted(self.overrides.items())],
                "settings": dict(sorted(self.settings.items()))}

    def snapshot(self) -> str:
        """sha256 of the canonical inputs (lesson 7.1.3): equal inputs, equal id."""
        text = json.dumps(self.inputs(), sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(text.encode("utf-8")).hexdigest()

    def to_json(self) -> str:
        """The whole record, inputs and metadata, as canonical JSON."""
        record = {"scenario_id": self.scenario_id, "name": self.name, "parent_id": self.parent_id,
                  "created_by": self.created_by, "created_at": self.created_at, **self.inputs()}
        return json.dumps(record, sort_keys=True, separators=(",", ":"))

    @classmethod
    def from_json(cls, text: str) -> "Scenario":
        r = json.loads(text)
        return cls(scenario_id=r["scenario_id"], name=r["name"],
                   data=DataRef(r["data"]["size"], r["data"]["seed"], r["data"]["hash"]),
                   budget={int(y): v for y, v in r["budget"].items()}, settings=dict(r["settings"]),
                   overrides={p: Override(p, k, y) for p, k, y in r["overrides"]},
                   parent_id=r["parent_id"], created_by=r["created_by"], created_at=r["created_at"])


def create(portfolio: Portfolio, size: str, scenario_id: str, name: str, by: str, at: str) -> Scenario:
    """A new scenario on GridCap's own budgets, with no overrides."""
    return Scenario(scenario_id, name, DataRef(size, portfolio.seed, portfolio.content_hash()),
                    budget=dict(portfolio.budget), settings=dict(SETTINGS), created_by=by, created_at=at)


def copy_scenario(s: Scenario, scenario_id: str, name: str, by: str, at: str) -> Scenario:
    """A new scenario with the same inputs as `s`, its own containers, and a link back to `s`."""
    return Scenario(scenario_id, name, s.data, budget=dict(s.budget), settings=dict(s.settings),
                    overrides=dict(s.overrides), parent_id=s.scenario_id, created_by=by, created_at=at)


def load_portfolio(ref: DataRef) -> Portfolio:
    """Regenerate the portfolio a scenario names, and refuse it if it is not the same data."""
    portfolio = generate(ref.size, ref.seed)
    if portfolio.content_hash() != ref.content_hash:
        raise ValueError(f"portfolio {ref.size}/{ref.seed} does not match the hash the scenario recorded")
    return portfolio


@dataclass(frozen=True)
class Result:
    """What one optimization of one scenario produced, tied to the inputs it used."""

    scenario_id: str
    snapshot: str
    status: str
    npv: float | None
    starts: dict[str, int]


def optimize(s: Scenario) -> Result:
    """Build the scenario's model from its data alone, solve it, and stamp the result with the snapshot."""
    portfolio = load_portfolio(s.data)
    bounds = {}
    for o in s.overrides.values():
        bounds.update(bounds_of(o, portfolio.project(o.project)))
    built = build(portfolio, s.budget, bounds)
    result = solve_highs(built.model, s.settings["relative_gap_tolerance"])
    status = result.termination.reason.name
    if result.termination.reason != mathopt.TerminationReason.OPTIMAL:
        return Result(s.scenario_id, s.snapshot(), status, None, {})
    starts = {pid: t for (pid, t), v in built.x.items() if result.variable_values(v) > 0.5}
    return Result(s.scenario_id, s.snapshot(), status, round(result.objective_value()), dict(sorted(starts.items())))


def diff_plans(a: Result, b: Result) -> dict[str, list]:
    """Selected, deferred and shifted from plan a to plan b, the three lists of lesson 9.3.3."""
    return {"selected": sorted(set(b.starts) - set(a.starts)),
            "deferred": sorted(set(a.starts) - set(b.starts)),
            "shifted": [f"{p} {a.starts[p]}->{b.starts[p]}" for p in sorted(set(a.starts) & set(b.starts))
                        if a.starts[p] != b.starts[p]]}


class Clock:
    """A clock that a program passes in, so a replayed run prints the same times."""

    def __init__(self, start: str = "2027-03-01T09:00Z", step_minutes: int = 5):
        self.hour, self.minute = int(start[11:13]), int(start[14:16])
        self.day, self.step = start[:10], step_minutes

    def now(self) -> str:
        stamp = f"{self.day}T{self.hour:02d}:{self.minute:02d}Z"
        self.minute += self.step
        self.hour, self.minute = self.hour + self.minute // 60, self.minute % 60
        return stamp
