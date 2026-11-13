"""Two ways to value a renewal, side by side: lesson 7.4.1's depth and lesson 7.3.4's age path.

Lesson 7.4.1 renews the asset at the start of its start year, to (1 - d) times its age, and counts
the expected failures it avoids to the end of the evaluation window. Lesson 7.3.4 lets the asset
age through the years of work, gives it a share rho of the age it had reached from the year after,
and counts year by year. This program counts expected failures (not dollars) both ways on GridCap
tiny, so the only differences left are the conventions themselves.
"""

from benefits import DEPTH, EVALUATION_YEARS, failures, failures_avoided
from gridcap import generate

#: Lesson 7.3.4's share of its age the asset keeps after the work (lesson 1.1.2's convention).
KEEP = {"replace": 0.0, "rebuild": 0.0, "underground": 0.0, "repair": 0.5, "trim": 0.5,
        "clear": 0.5, "widen": 0.5}


def failures_by_age_path(asset, window, start: int, duration: int, keep: float) -> float:
    """Expected failures avoided over the window, year by year, on lesson 7.3.4's age path."""
    first, done = window[0], start + duration
    total = 0.0
    for y in window:
        before = asset.age + (y - first)
        after = before if y < done else keep * (asset.age + (done - first)) + (y - done)
        total += (failures(before, asset.weibull_beta, asset.weibull_eta, 1)
                  - failures(after, asset.weibull_beta, asset.weibull_eta, 1))
    return total


tiny = generate("tiny")
window = tuple(range(tiny.years[0], tiny.years[0] + EVALUATION_YEARS))
print("expected failures avoided over 2027-2036, each project started as early as it can")
print("project action      work  d    1-d  rho  | 7.4.1   path, no work time  path, 1-d  path, rho (7.3.4)")
for p in tiny.projects:
    a, s = tiny.asset(p.asset_id), p.earliest_start
    d, rho = DEPTH[p.intervention], KEEP[p.intervention]
    print(f"{p.project_id}    {p.intervention:11} {p.duration}y  {d:.1f}  {1 - d:.1f}  {rho:.1f}  | "
          f"{failures_avoided(tiny, p, s):5.3f}   {failures_by_age_path(a, window, s, 0, 1 - d):5.3f}"
          f"               {failures_by_age_path(a, window, s, p.duration, 1 - d):5.3f}      "
          f"{failures_by_age_path(a, window, s, p.duration, rho):5.3f}")
