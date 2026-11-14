"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")

from pydantic import ValidationError

from trim_result import TrimResult

plan = {"status": "time_limit", "message": "Stopped at the 60 s limit.", "value": 150.0, "bound": 180.0,
        "gap": 0.2, "circuits": ["L-3", "L-5"],
        "hours_by_month": [{"month": 6, "crew_hours": 90, "capacity": 100},
                           {"month": 9, "crew_hours": 40, "capacity": 100}]}


def check(**changes):
    try:
        TrimResult(**{**plan, **changes})
        return "accepted"
    except ValidationError as e:
        return "refused: " + e.errors()[0]["msg"]


print("time_limit plan:", check())
print("status infeasible, circuits kept:", check(status="infeasible"))
print("bound None, gap 0.2:", check(bound=None))
print("June 110 hours of 100:", check(hours_by_month=[{"month": 6, "crew_hours": 110, "capacity": 100}]))
print("months 9 then 6:", check(hours_by_month=plan["hours_by_month"][::-1]))
