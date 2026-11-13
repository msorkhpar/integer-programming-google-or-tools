from __future__ import annotations

from ortools.math_opt.python import mathopt

# sites[name] = (value per generator-hour in $k, hours the site can use, hookup fee in $k)
Sites = dict[str, tuple[float, float, float]]


def build(sites: Sites, fleet: float, big_m: dict[str, float], integer: bool = True):
    """Generator-hours per site, a hookup binary per site, and the fleet's total hours."""
    model = mathopt.Model(name="generators")
    hours = {s: model.add_variable(lb=0, name=f"hours_{s}") for s in sites}
    hook = {s: model.add_variable(lb=0, ub=1, is_integer=integer, name=f"hook_{s}") for s in sites}
    for s, (_, demand, _) in sites.items():
        model.add_linear_constraint(hours[s] <= demand, name=f"demand_{s}")
    model.add_linear_constraint(sum(hours.values()) <= fleet, name="fleet")
    for s in sites:
        model.add_linear_constraint(hours[s] <= big_m[s] * hook[s], name=f"hookup_{s}")
    model.maximize(sum(v * hours[s] for s, (v, _, _) in sites.items())
                   - sum(fee * hook[s] for s, (_, _, fee) in sites.items()))
    return model, hours, hook


def tight_m(sites: Sites, fleet: float) -> dict[str, float]:
    """The smallest M for each site's hookup row that the demand and fleet rows justify."""
    return {s: min(demand, fleet) for s, (_, demand, _) in sites.items()}


def bounds(sites: Sites, fleet: float) -> dict[str, float]:
    """The LP bound with M = 1e6, the LP bound with the tight M, and the MILP optimum."""
    loose = {s: 1e6 for s in sites}
    tight = tight_m(sites, fleet)
    return {
        "loose": mathopt.solve(build(sites, fleet, loose, integer=False)[0], mathopt.SolverType.GLOP).objective_value(),
        "tight": mathopt.solve(build(sites, fleet, tight, integer=False)[0], mathopt.SolverType.GLOP).objective_value(),
        "milp": mathopt.solve(build(sites, fleet, tight)[0], mathopt.SolverType.HIGHS).objective_value(),
    }


if __name__ == "__main__":
    sites = {"A": (40, 30, 500), "B": (25, 80, 300), "C": (30, 50, 900)}
    print(tight_m(sites, 100))
    print(bounds(sites, 100))
