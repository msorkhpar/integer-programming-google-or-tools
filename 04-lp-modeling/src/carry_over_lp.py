"""The program split over GridCap small's five years, with and without carry-over (fictional data)."""

from ortools.math_opt.python import mathopt

from gridcap import PROGRAMS
from program_split import CREW, FLOOR, SHARE, VALUE, small

YEARS = small.years
RATE = small.discount_rate


def build_years(carry: bool):
    model = mathopt.Model(name="program split, five years")
    s = {(k, y): model.add_variable(lb=0, name=f"s_{k}_{y}") for k in PROGRAMS for y in YEARS}
    r = {y: model.add_variable(lb=0, name=f"r_{y}") for y in YEARS} if carry else {}
    spend = {y: sum(s[k, y] for k in PROGRAMS) for y in YEARS}
    for i, y in enumerate(YEARS):
        if carry:
            incoming = r[YEARS[i - 1]] if i else 0
            model.add_linear_constraint(spend[y] + r[y] <= small.budget[y] + incoming, name=f"cash_{y}")
        else:
            model.add_linear_constraint(spend[y] <= small.budget[y], name=f"budget_{y}")
        for k in PROGRAMS:
            model.add_linear_constraint(CREW[k] / 1000 * s[k, y] <= small.crews[k, y], name=f"crew_{k}_{y}")
            model.add_linear_constraint(s[k, y] <= SHARE * spend[y], name=f"share_{k}_{y}")
        for k, amount in FLOOR.items():
            model.add_linear_constraint(s[k, y] >= amount, name=f"floor_{k}_{y}")
    # A dollar of value earned in a later year is worth less today: discount it to the first year.
    model.maximize(sum(VALUE[k] / (1 + RATE) ** (y - YEARS[0]) * s[k, y] for k in PROGRAMS for y in YEARS))
    return model, s, r


if __name__ == "__main__":
    for carry in (False, True):
        model, s, r = build_years(carry)
        result = mathopt.solve(model, mathopt.SolverType.GLOP)
        print(f"{'with' if carry else 'no'} carry-over: {result.termination.reason.name}, "
              f"NPV {result.objective_value():,.1f}")
        for y in YEARS:
            spent = sum(result.variable_values(s[k, y]) for k in PROGRAMS)
            out = f"  carried out {result.variable_values(r[y]):7,.1f}" if carry else ""
            print(f"  {y}: budget {small.budget[y]:5,}  spent {spent:9,.1f}{out}")
