"""Lesson 13.1.5: the model's properties on 200 drawn portfolios, and on a model with a planted bug.

The planted bug is a builder that reads every lag as 0, a slip a refactor can make. The drawn
portfolios are invented test data, not GridCap.
"""

from __future__ import annotations

from dataclasses import replace

from hypothesis import given

from cipt_model import build
from cipt_properties import CI, portfolios, holds

seen = []


@CI
@given(portfolios())
def test_every_property(case):
    seen.append(len(case.portfolio.projects))
    holds(case)


def no_lags(pf):
    """The planted bug: the builder sees every parent lag as 0."""
    return build(replace(pf, projects=tuple(replace(p, parent_lag=0) for p in pf.projects)))


def crews_late(pf):
    """The planted bug: crew-months charged to the start year only, not to every year of work."""
    b = build(pf)
    for name in [n for n in b.rules if n.startswith("crews_")]:
        b.model.delete_linear_constraint(b.rules.pop(name))
    use = {k: 0 for k in pf.crews}
    terms = {k: [] for k in pf.crews}
    for (pid, t), x in b.x.items():
        p = pf.project(pid)
        terms[p.program, t].append(p.crew_months * x)
    for (g, y), limit in pf.crews.items():
        if terms[g, y]:
            b.add(f"crews_{g}_{y}", sum(terms[g, y]) <= limit)
    return b


@CI
@given(portfolios())
def test_with_lags_ignored(case):
    holds(case, builder=no_lags)


@CI
@given(portfolios())
def test_with_crews_in_start_year(case):
    holds(case, builder=crews_late)


if __name__ == "__main__":
    test_every_property()
    print(f"correct model: every property held on {len(seen)} drawn portfolios "
          f"({min(seen)} to {max(seen)} projects)")
    for label, test in (("lags read as 0", test_with_lags_ignored),
                        ("crews charged to the start year", test_with_crews_in_start_year)):
        try:
            test()
            print(f"{label}: no property failed")
        except AssertionError as error:
            print(f"{label}: a property failed: {str(error).splitlines()[0]}")
