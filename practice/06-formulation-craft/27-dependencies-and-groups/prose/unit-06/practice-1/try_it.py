"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")

from docks import Vessel, apply_overrides, build, undo_overrides

# Three ferries, docking years 2027 to 2030.
vessels = [Vessel("TERN", (2027, 2028, 2029, 2030)), Vessel("GULL", (2028, 2029)),
           Vessel("KITE", (2027, 2028, 2029, 2030))]
overrides = [("lock", "TERN", 2028), ("ban", "GULL"), ("by", "KITE", 2028)]


def bounds(x):
    return {f"{v} {t}": (var.lower_bound, var.upper_bound) for (v, t), var in sorted(x.items())}


model, x = build(vessels)
before = bounds(x)
changes = apply_overrides(x, vessels, overrides)
after = bounds(x)
for key in ("TERN 2027", "TERN 2028", "GULL 2029", "KITE 2028", "KITE 2030"):
    print(f"{key} bounds after overrides:", after[key])
undo_overrides(changes)
print("bounds back after undo:", bounds(x) == before)
