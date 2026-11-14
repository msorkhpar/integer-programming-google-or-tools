"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")

from scenarios import build, run_scenarios

model, rows = build()
scenarios = [{}, {"budget": 16}, {"staff": 7}, {"budget": 16, "staff": 11}, {"budget": 4}]
for scenario, value in zip(scenarios, run_scenarios(model, rows, scenarios)):
    print(f"scenario {scenario}:", value)
print("bounds after the runs:", rows["budget"].upper_bound, rows["staff"].upper_bound)
