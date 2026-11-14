"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")

from whatif import Plan, Project, diff, solve, what_if

pipes = [
    Project("P-1", (200, 100), {2030: 600, 2031: 550}),
    Project("P-2", (150,), {2030: 300, 2031: 280, 2032: 260}),
    Project("P-3", (250,), {2031: 420, 2032: 390}),
    Project("P-4", (100,), {2032: 140}),
]
base = Plan("S-1", {2030: 400, 2031: 400, 2032: 400})

print("base plan:", solve(base, pipes))
trial, changes = what_if(base, "S-2", {"P-1": ("start_in", 2031), "P-4": ("out", None)}, pipes)
print("trial S-2 overrides:", trial.overrides, "parent", trial.parent_id)
print("trial plan:", solve(trial, pipes))
print("diff base to trial:", changes)
print("diff of two small plans:", diff({"P-2": 2030}, {"P-2": 2032, "P-3": 2031}))
