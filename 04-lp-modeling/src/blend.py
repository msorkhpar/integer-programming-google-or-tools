"""Blending: buy tree-trimming hours from three contractors so the average rework rate meets a target.

The contractors and their numbers are invented for this course, like the rest of GridCap.
"""

from ortools.math_opt.python import mathopt

#: contractor -> ($ per crew-hour, rework rate in %, hours it can supply)
CONTRACTORS = {"Northline": (95, 2.0, 10_000), "Birch & Sons": (78, 5.5, 12_000), "Canopy Co": (70, 7.0, 10_000)}
HOURS = 20_000          # crew-hours of trimming GridCap needs this season
TARGET = 4.0            # the average rework rate may be at most 4.0%


def buy(blend: bool, per_contractor: bool = False):
    model = mathopt.Model(name="trimming blend")
    h = {c: model.add_variable(lb=0, ub=cap, name=f"h_{c}") for c, (_, _, cap) in CONTRACTORS.items()}
    model.add_linear_constraint(sum(h.values()) == HOURS, name="hours")
    if blend:
        # average rework <= TARGET, multiplied out by the total hours:  sum (q_c - TARGET) h_c <= 0
        model.add_linear_constraint(sum((q - TARGET) * h[c] for c, (_, q, _) in CONTRACTORS.items()) <= 0,
                                    name="rework")
    if per_contractor:
        # the misreading: every contractor at or under the target, so only they may be hired
        for c, (_, q, _) in CONTRACTORS.items():
            if q > TARGET:
                model.add_linear_constraint(h[c] == 0, name=f"exclude_{c}")
    model.minimize(sum(rate * h[c] for c, (rate, _, _) in CONTRACTORS.items()))
    return model, h


def show(label: str, model, h) -> None:
    result = mathopt.solve(model, mathopt.SolverType.GLOP)
    if result.termination.reason != mathopt.TerminationReason.OPTIMAL:
        print(f"{label:22} {result.termination.reason.name}")
        return
    hours = {c: result.variable_values(v) for c, v in h.items()}
    rework = sum(CONTRACTORS[c][1] * x for c, x in hours.items()) / HOURS
    print(f"{label:22} cost ${result.objective_value():,.0f}  rework {rework:.2f}%  "
          + "  ".join(f"{c} {x:,.0f}" for c, x in hours.items()))


if __name__ == "__main__":
    show("cheapest, no rule", *buy(blend=False))
    show("average rework <= 4%", *buy(blend=True))
    show("each contractor <= 4%", *buy(blend=False, per_contractor=True))
