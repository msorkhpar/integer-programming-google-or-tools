"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")

# Pyomo logs every set it builds and the whole solver log; keep its own logger to warnings.
logging.getLogger("pyomo").setLevel(logging.WARNING)

from trim import Circuit, trim_plan

# Circuit(crew hours, risk removed, months it may be trimmed in)
circuits = {"G1": Circuit(50, 6.0, ("Mar", "Apr")), "G2": Circuit(40, 5.5, ("Mar",)),
            "G3": Circuit(30, 4.0, ("Apr", "May")), "G4": Circuit(45, 6.5, ("May",))}
for hours in ({"Mar": 90, "Apr": 50, "May": 50}, {"Mar": 50, "Apr": 30, "May": 40}):
    value, plan = trim_plan(circuits, hours)
    print(f"crew hours {hours}: risk removed {round(value, 2)}, months {plan}")
