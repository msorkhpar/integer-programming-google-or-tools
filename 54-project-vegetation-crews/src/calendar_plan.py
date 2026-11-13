"""Lesson 14.1.5: the small season with access windows, crews' weeks off and must-trim circuits.

A checker written from the planner's rules (it shares no code with the model) reads a plan and lists
every calendar rule it breaks. It runs on the plan of steps/04, which never saw the calendars (solved
as in risk_plan.py, so that it repeats), and on the plan of steps/05, whose planner runs here with
WORKERS set to 1: it proves its plan optimal well inside its time limit, so the output repeats.
"""

from snapshots import solve_repeatably, use

use(4)
from vegcrew import planner as planner_4             # noqa: E402
from vegcrew.data import season_from_dict as load_4  # noqa: E402
from vegcrew.generate import scenario as scenario_4  # noqa: E402



use(5)
from vegcrew import planner                        # noqa: E402
from vegcrew.data import season_from_dict          # noqa: E402
from vegcrew.generate import scenario              # noqa: E402
from vegcrew.report import format_plan             # noqa: E402

raw = scenario("small")
season = season_from_dict(raw)


def broken(raw: dict, trims: dict) -> list[str]:
    """Every calendar rule the trims break, read straight from the inventory rows."""
    found = []
    for row in raw["circuits"]:
        t = trims.get(row["id"])
        if t is None:
            if row["must"]:
                found.append(f"{row['id']} is a must and is not trimmed")
            continue
        last = t.end - 1
        if row["windows"] and not any(a <= t.start and last <= b for a, b in row["windows"]):
            found.append(f"{row['id']} weeks {t.start}-{last} are outside its windows {row['windows']}")
        for a, b in raw["crew_off"].get(t.crew, []):
            if t.start <= b and a <= last:
                found.append(f"{row['id']} weeks {t.start}-{last} on {t.crew}, who is off weeks {a}-{b}")
    return found


print("calendars:", ", ".join(f"{k} off weeks {a}-{b}" for k, spans in raw["crew_off"].items() for a, b in spans))
print("must:", " ".join(c["id"] for c in raw["circuits"] if c["must"]),
      "| windows:", sum(1 for c in raw["circuits"] if c["windows"]), "of", len(raw["circuits"]), "circuits")
old, _ = solve_repeatably(planner_4, load_4(scenario_4("small")))
problems = broken(raw, old.trims)
print(f"steps/04 plan ({old.status}): {len(problems)} calendar rules broken")
for line in problems:
    print("  " + line)
planner.WORKERS = 1
plan = planner.make_plan(season)
print(format_plan(season, plan))
print(f"steps/05 plan: {len(broken(raw, plan.trims))} calendar rules broken")
