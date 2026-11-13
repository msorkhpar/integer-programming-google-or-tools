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
    tm = TrimModel(cp_model.CpModel())
    h = horizon(season)
    deferred = h + DEFER_WEEKS                      # the end week of a circuit left for next season
    for c in season.circuits:
        t = tm.trimmed[c.cid] = tm.model.new_bool_var(f"t_{c.cid}")
        e = tm.end[c.cid] = tm.model.new_int_var_from_domain(
            cp_model.Domain.from_intervals([[c.weeks, h], [deferred, deferred]]), f"e_{c.cid}")
        starts = start_domain(c, h)
        options = [] if starts.is_empty() else crew_ids(season)    # no window fits it: no options
        for k in options:
            p = tm.present[c.cid, k] = tm.model.new_bool_var(f"p_{c.cid}_{k}")
            s = tm.start[c.cid, k] = tm.model.new_int_var_from_domain(starts, f"s_{c.cid}_{k}")   # window_c
            tm.work[c.cid, k] = tm.model.new_optional_fixed_size_interval_var(s, c.weeks, p, f"w_{c.cid}_{k}")
            tm.model.add(e == s + c.weeks).only_enforce_if(p)                        # ends_c,k
        tm.model.add(sum(tm.present[c.cid, k] for k in options) == t)               # once_c
        tm.model.add(e == deferred).only_enforce_if(~t)                              # waits_c
        if c.must:
            overdue = tm.rule(f"must_{c.cid}", f"{c.cid} is overdue and must be trimmed this season")
            tm.model.add(t == 1).only_enforce_if(overdue)                            # must_c
        table = [c.carried(week) for week in range(deferred + 1)]
        tm.carried[c.cid] = tm.model.new_int_var(0, table[-1], f"r_{c.cid}")
        tm.model.add_element(e, table, tm.carried[c.cid])                            # risk_c
    for k in crew_ids(season):
        off = [tm.model.new_fixed_size_interval_var(first, last - first + 1, f"off_{k}_{first}")
               for first, last in season.crew_off.get(k, ())]
        tm.model.add_no_overlap([w for (_, crew), w in tm.work.items() if crew == k] + off)   # crew_k
    tm.model.add(sum(c.cost * tm.trimmed[c.cid] for c in season.circuits) <= season.budget).only_enforce_if(
        tm.rule("budget", f"the season's budget is ${season.budget:,}k"))                # budget
    for i, o in enumerate(overrides, start=1):
        on = tm.rule(f"override_{i}", f"override {i}: {o.says()}")
        t = tm.trimmed[o.cid]
        if o.kind == "skip":
            tm.model.add(t == 0).only_enforce_if(on)                                 # override_i
            continue
        tm.model.add(t == 1).only_enforce_if(on)                                     # pin and force
        if o.crew and (o.cid, o.crew) in tm.present:
            tm.model.add(tm.present[o.cid, o.crew] == 1).only_enforce_if(on)
        if o.start is not None:
            tm.model.add(tm.end[o.cid] == o.start + season.circuit(o.cid).weeks).only_enforce_if(on)
    tm.model.minimize(sum(tm.carried.values()))
    return tm
