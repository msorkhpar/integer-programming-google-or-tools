"""Reading a two-objective frontier the way a planner does: lookups, prices of each step, knees.

Generic like `frontier.py`: a Point's `first` is the objective the planner wants more of (risk
removed, or value), `second` the one paid with (NPV, or minus the budget). Both are maximized.
"""

from __future__ import annotations

from dataclasses import dataclass

from frontier import TOL, Point


def best_reaching(points: list[Point], target: float) -> Point | None:
    """The frontier point with the most `second` among those with `first` >= target."""
    reaching = [p for p in points if p.first >= target - TOL]
    return max(reaching, key=lambda p: p.second) if reaching else None


@dataclass(frozen=True)
class Step:
    """Moving from point a to point b along the frontier: `gain` of first, paid with `cost` of second."""
    a: Point
    b: Point

    @property
    def gain(self) -> float:
        return self.b.first - self.a.first

    @property
    def cost(self) -> float:
        return self.a.second - self.b.second

    @property
    def price(self) -> float:
        """Units of `second` given up per unit of `first` gained."""
        return self.cost / self.gain


def steps(points: list[Point]) -> list[Step]:
    """The steps between consecutive points, ordered by `first` increasing."""
    ordered = sorted(points, key=lambda p: p.first)
    return [Step(a, b) for a, b in zip(ordered, ordered[1:])]


def knees(hull: list[Point], ratio: float = 2.0) -> list[tuple[Point, float, float]]:
    """Hull points where the price of the next step is at least `ratio` times the price of the last.

    Returns (point, price before, price after) for each. Pass the supported points: along them the
    price can only rise, so a knee is where it rises sharply.
    """
    s = steps(hull)
    return [(before.b, before.price, after.price) for before, after in zip(s, s[1:])
            if after.price >= ratio * before.price]
