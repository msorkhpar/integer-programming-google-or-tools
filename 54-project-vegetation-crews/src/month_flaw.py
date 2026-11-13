"""Lesson 14.1.3: what the month model promises that one crew cannot do, and what it refuses that one
crew can, on two hand-made seasons, solved by the month model (steps/02) and the interval model (steps/03)."""

from snapshots import use


def one_circuit(weeks, crews, months):
    return {"budget": 100, "crews": crews, "months": months, "circuits": [
        {"id": "A", "region": "North", "miles": 30, "cost": 50, "risk": 200, "weeks": weeks, "growth": 0}]}


cases = [("a 6-week trim, 1 crew, 2 months", one_circuit(6, 1, 2)),
         ("a 6-week trim, 2 crews, 1 month", one_circuit(6, 2, 1))]
for step, label in [(2, "month model   "), (3, "interval model")]:
    use(step)
    from vegcrew.data import season_from_dict
    from vegcrew.planner import make_plan
    for name, raw in cases:
        trim = make_plan(season_from_dict(raw)).trims.get("A")
        if trim is None:
            said = "not trimmed"
        elif step == 2:
            said = f"trimmed in month {trim.month}"
        else:
            said = f"trimmed by {trim.crew} in weeks {trim.start}-{trim.end - 1}"
        print(f"{label}  {name}: {said}")

use(2)
from vegcrew.data import WEEKS_PER_MONTH, season_from_dict   # noqa: E402
from vegcrew.generate import scenario                         # noqa: E402
from vegcrew.planner import make_plan                         # noqa: E402

season = season_from_dict(scenario("small"))
plan = make_plan(season)
print(f"month model on the small season, {season.crews} crews, {WEEKS_PER_MONTH}-week months:")
for cid, trim in sorted(plan.trims.items(), key=lambda kv: kv[1].month):
    weeks = season.circuit(cid).weeks
    if weeks > WEEKS_PER_MONTH:
        print(f"  {cid} needs {weeks} crew-weeks in month {trim.month}: only by splitting it across "
              f"{-(-weeks // WEEKS_PER_MONTH)} crews")
