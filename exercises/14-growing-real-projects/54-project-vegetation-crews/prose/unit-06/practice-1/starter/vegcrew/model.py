"""The CP-SAT model of a season: every trim an optional interval on one crew, every planner's rule
behind a named literal so that a failed plan can say which rules clash."""

from __future__ import annotations

from dataclasses import dataclass, field

from ortools.sat.python import cp_model

from vegcrew.data import DEFER_WEEKS, WEEKS_PER_MONTH, Circuit, Override, Season


def crew_ids(season: Season) -> list[str]:
    return [f"K{k}" for k in range(1, season.crews + 1)]


def horizon(season: Season) -> int:
    return season.months * WEEKS_PER_MONTH


@dataclass
class TrimModel:
    model: cp_model.CpModel
    trimmed: dict[str, cp_model.IntVar] = field(default_factory=dict)                 # circuit
    present: dict[tuple[str, str], cp_model.IntVar] = field(default_factory=dict)    # (circuit, crew)
    start: dict[tuple[str, str], cp_model.IntVar] = field(default_factory=dict)
    work: dict[tuple[str, str], cp_model.IntervalVar] = field(default_factory=dict)
    end: dict[str, cp_model.IntVar] = field(default_factory=dict)                     # circuit
    carried: dict[str, cp_model.IntVar] = field(default_factory=dict)                 # circuit
    rules: dict[str, cp_model.IntVar] = field(default_factory=dict)                   # name -> literal
    says: dict[str, str] = field(default_factory=dict)                                # name -> words

    def rule(self, name: str, says: str) -> cp_model.IntVar:
        """A literal that switches one of the planner's rules on; the rows it guards hold only if it is 1."""
        self.rules[name] = self.model.new_bool_var(name)
        self.says[name] = says
        return self.rules[name]


def start_domain(c: Circuit, h: int) -> cp_model.Domain:
    """Every first week that keeps the trim inside one of the circuit's windows and the season."""
    windows = c.windows or ((0, h - 1),)
    return cp_model.Domain.from_intervals(
        [[first, min(last, h - 1) - c.weeks + 1] for first, last in windows
         if min(last, h - 1) - c.weeks + 1 >= first])


def build(season: Season, overrides: tuple[Override, ...] = ()) -> TrimModel:
    """The model of the lesson before, moved to model.py with crew_ids, horizon and start_domain, and built with the overrides. Every rule a planner can change sits behind a named literal, with its words: `must_<cid>` (`<cid> is overdue and must be trimmed this season`), budget (`the season's budget is $<budget>k`, the budget written with a thousands comma, as f"{budget:,}" writes it: `$962k`, `$1,000k`) and `override_<i>` (`override <i>: ` followed by the override's own words, as Override.says gives them: `trim <cid> on <crew> from week <start> (<reason>)` for a pin, `leave <cid> for next season (<reason>)`, `trim <cid> this season (<reason>)`, with `no reason given` when the reason is empty). A skip leaves its circuit untrimmed; a pin or force trims it; a pin also fixes the crew and the first week it names. The rules are made in this order: each must as its circuit comes in the season's order, then the budget, then the overrides in the order given."""
    return None
