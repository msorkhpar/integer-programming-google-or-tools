"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")
from why import cost_interval, forcing_cost, refused_by


def project(program, region, cost, first, last, npv, must=False, group=None, crews=1):
    return {"program": program, "region": region, "cost": cost, "earliest": first, "latest": last,
            "must": must, "parent": None, "lag": 0, "group": group, "crews": crews, "npv": npv}


# Invented portfolio over two years, money in $k.
snapshot = {
    "years": [2031, 2032], "rate": 0.04,
    "budget": {2031: 400, 2032: 250},
    "region_budget": {"East": {2031: 400, 2032: 400}, "West": {2031: 400, 2032: 400}},
    "crews": {"lines": {2031: 5, 2032: 5}, "poles": {2031: 3, 2032: 3}},
    "floor": {"East": 0, "West": 0},
    "projects": {
        "Q1": project("lines", "East", [180], 2031, 2032, {2031: 70, 2032: 60}, must=True, crews=2),
        "Q2": project("lines", "East", [120], 2031, 2031, {2031: 50}, must=True, crews=2),
        "Q3": project("poles", "West", [200], 2031, 2032, {2031: 55, 2032: 50}),
        "Q4": project("poles", "West", [150], 2031, 2032, {2031: 45, 2032: 42}, crews=2),
    },
}

plan = {"Q1": 2032, "Q2": 2031, "Q3": 2031}
print("Q4 added to Q1 2032, Q2 2031, Q3 2031:", refused_by(snapshot, {"name": "base"}, plan, "Q4"))
forced = forcing_cost(snapshot, {"name": "base"}, "Q4")
print("forcing Q4, cost:", None if forced is None else round(forced.cost, 2))
print("forcing Q4, gives way:", None if forced is None else forced.gives_way)
print("interval for primals 300/280, bounds 310/290:", cost_interval(300.0, 310.0, 280.0, 290.0))
