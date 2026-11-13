"""Lesson 6.5.4: start years that a lag rules out, removed before the model is built.

GridCap is a fictional utility's portfolio. The lags are read as finish-to-start, and P023 is
also given a maximum lag of 1 year, so that some start years can never be used.
"""

from gridcap import generate

small = generate("small")


def usable_years(parent_starts, child_starts, low: int, high: int | None) -> tuple[list[int], list[int]]:
    """Start years of each project that some start year of the other can pair with."""
    def fits(s, t):
        return t - s >= low and (high is None or t - s <= high)
    child = [t for t in child_starts if any(fits(s, t) for s in parent_starts)]
    parent = [s for s in parent_starts if any(fits(s, t) for t in child_starts)]
    return parent, child


cases = [("P015", "P016", "finish-to-start, lag 0", 1, None),
         ("P022", "P023", "start-to-start, lag 1 to 1", 1, 1),
         ("P022", "P023", "finish-to-start, lag 0", 3, None)]
for parent_id, child_id, label, low, high in cases:
    p, c = small.project(parent_id), small.project(child_id)
    parent, child = usable_years(list(p.starts()), list(c.starts()), low, high)
    print(f"{child_id} after {parent_id} ({label}): {child_id} {list(c.starts())} -> {child}, "
          f"{parent_id} {list(p.starts())} -> {parent} (if {child_id} is funded)")
