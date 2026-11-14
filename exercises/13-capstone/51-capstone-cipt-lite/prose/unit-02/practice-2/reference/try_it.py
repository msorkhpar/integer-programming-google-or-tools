"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")
from portfolio_model import allows, best

def project(program, region, cost, first, last, npv, must=False, parent=None, lag=0, group=None, crews=1):
    return {"program": program, "region": region, "cost": cost, "earliest": first, "latest": last,
            "must": must, "parent": parent, "lag": lag, "group": group, "crews": crews, "npv": npv}


# Four invented feeder projects over two years. Money in $k.
snap = {
    "years": [2030, 2031], "rate": 0.04,
    "budget": {2030: 200, 2031: 150},
    "region_budget": {"East": {2030: 200, 2031: 200}, "West": {2030: 120, 2031: 120}},
    "crews": {"lines": {2030: 2, 2031: 2}, "poles": {2030: 2, 2031: 2}},
    "floor": {"East": 50, "West": 0},
    "projects": {
        "F1": project("lines", "East", [100, 30], 2030, 2030, {2030: 60}, must=True),
        "F2": project("lines", "East", [70], 2030, 2031, {2030: 35, 2031: 32}, parent="F1", lag=1),
        "F3": project("poles", "West", [90], 2030, 2031, {2030: 40, 2031: 38}, group="A"),
        "F4": project("poles", "West", [60], 2030, 2031, {2030: 30, 2031: 27}, group="A"),
    },
}

value, plan = best(snap)
print("best value:", round(value, 2))
print("best plan:", plan)
print("allows F1 2030, F2 2031:", allows(snap, {"F1": 2030, "F2": 2031}))
print("allows F1 2030, F3 2030, F4 2031:", allows(snap, {"F1": 2030, "F3": 2030, "F4": 2031}))
print("allows F2 2031 alone:", allows(snap, {"F2": 2031}))
