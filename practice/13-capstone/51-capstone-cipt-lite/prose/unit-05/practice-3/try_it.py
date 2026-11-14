"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")
from warm_start import build, carry, check, hint, plan_of, repair, solve


def job(cost, earliest, latest, npv, must=False, parent=None, lag=0):
    return {"cost": cost, "earliest": earliest, "latest": latest, "must": must, "parent": parent, "lag": lag,
            "group": None, "npv": dict(zip(range(earliest, latest + 1), npv))}


snapshot = {"years": [2031, 2032], "budget": {2031: 200, 2032: 200}, "projects": {
    "R1": job([120], 2031, 2032, [50, 44], must=True),
    "R2": job([90], 2031, 2032, [30, 27]),
    "R3": job([60], 2031, 2031, [33]),
    "R4": job([40], 2032, 2032, [15], parent="R2", lag=1),
}}
last = {"R1": 2031, "R2": 2031, "R3": 2031, "R4": 2032, "R8": 2031}

carried = carry(last, snapshot)
print("carried from last cycle:", carried, "breaks:", check(snapshot, carried))
start = repair(snapshot, carried)
print("repaired start:", start, "breaks:", check(snapshot, start))
model, x = build(snapshot)
result = solve(model, hint(x, start))
print("hinted solve:", result.termination.reason.name, round(result.objective_value(), 2), plan_of(x, result))
