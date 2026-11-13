from __future__ import annotations

from dataclasses import dataclass, field

from ortools.math_opt.python import mathopt


@dataclass(frozen=True)
class Job:
    jid: str
    earliest: int                  # first year the job may be done
    latest: int                    # last year the job may be done
    weeks: dict = field(default_factory=dict)    # crew -> weeks that crew needs for the job
    large: bool = False            # a large-diameter main: certified crews only


@dataclass(frozen=True)
class Crew:
    cid: str
    weeks: dict                    # year -> weeks the crew is free that year
    rate: int                      # $k per week
    certified: bool = False


def build(jobs: list[Job], crews: list[Crew], years: list[int]) -> tuple[mathopt.Model, dict]:
    """Every job done once, by one crew in one year: in its window, by a crew allowed to, within the crew's weeks."""
    model = mathopt.Model(name="crews-and-years")
    x = {(j.jid, c.cid, t): model.add_binary_variable(name=f"x_{j.jid}_{c.cid}_{t}")
         for j in jobs for c in crews for t in years
         if j.earliest <= t <= j.latest and (c.certified or not j.large)}
    for j in jobs:
        model.add_linear_constraint(sum(v for (jid, _, _), v in x.items() if jid == j.jid) == 1, name=f"once_{j.jid}")
    for c in crews:
        for t in years:
            model.add_linear_constraint(
                sum(j.weeks[c.cid] * x[j.jid, c.cid, t] for j in jobs if (j.jid, c.cid, t) in x) <= c.weeks[t],
                name=f"weeks_{c.cid}_{t}")
    model.minimize(sum(c.rate * j.weeks[c.cid] * x[j.jid, c.cid, t]
                       for j in jobs for c in crews for t in years if (j.jid, c.cid, t) in x))
    return model, x


if __name__ == "__main__":
    crews = [Crew("K1", {2027: 20, 2028: 20}, 9, certified=True)]
    model, x = build([Job("J1", 2027, 2028, {"K1": 8}, large=True)], crews, [2027, 2028])
    print(len(x), "variables")
