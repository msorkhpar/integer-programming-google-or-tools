"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")
from overrides import Project, build

projects = [Project("D1", (2031, 2032, 2033)), Project("D2", (2031, 2032)), Project("D3", (2032, 2033))]


def bounds(overrides):
    try:
        model, x = build(projects, overrides)
    except ValueError as error:
        return f"refused: {error}"
    rows = [c.name for c in model.linear_constraints()]
    return {f"{p} {t}": (v.lower_bound, v.upper_bound) for (p, t), v in x.items()}, rows


print("start_in D1 2032, never D2:", bounds([("start_in", "D1", 2032), ("never", "D2")]))
print("not_before D1 2033, fund D3:", bounds([("not_before", "D1", 2033), ("fund", "D3")]))
print("start_in D2 2033:", bounds([("start_in", "D2", 2033)]))
print("start_in D3 2032, never D3:", bounds([("start_in", "D3", 2032), ("never", "D3")]))
