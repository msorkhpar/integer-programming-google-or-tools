"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")

from imaging import Replacement, plan_score, project_score

reference = {"downtime_hours": 50, "scans_per_day": 20, "energy_mwh": 200}
weights = {"downtime_hours": 0.4, "scans_per_day": 0.4, "energy_mwh": 0.2}
projects = {
    "Mammo": Replacement("Mammo", {"downtime_hours": 60, "scans_per_day": 30, "energy_mwh": 90},
                         {"downtime_hours": 35, "scans_per_day": 40, "energy_mwh": 70}),
    "Fluoro": Replacement("Fluoro", {"downtime_hours": 30, "scans_per_day": 15, "energy_mwh": 100},
                          {"downtime_hours": 20, "scans_per_day": 15, "energy_mwh": 140}),
}

for name, p in projects.items():
    print(f"{name} score:", round(project_score(p, reference, weights), 4))
print("plan Mammo + Fluoro:", round(plan_score(["Mammo", "Fluoro"], projects, reference, weights), 4))
print("empty plan:", plan_score([], projects, reference, weights))
