"""Cover inequalities for one budget row  sum a_i x_i <= b  over binary x, and a round of cuts."""

from __future__ import annotations

from ortools.math_opt.python import mathopt

EPS = 1e-9


def is_cover(cover: list[str], a: dict[str, float], b: float) -> bool:
    """A cover is a set of items whose weights add up to more than the row's right-hand side."""
    return sum(a[i] for i in cover) > b


def is_minimal(cover: list[str], a: dict[str, float], b: float) -> bool:
    """Minimal: a cover, and dropping any one item leaves a set that fits."""
    return is_cover(cover, a, b) and all(not is_cover([j for j in cover if j != i], a, b) for i in cover)


def violation(cover: list[str], x: dict[str, float]) -> float:
    """How far x breaks  sum_{i in C} x_i <= |C| - 1; positive means the cut removes x."""
    return sum(x[i] for i in cover) - (len(cover) - 1)


def separate(a: dict[str, float], b: float, x: dict[str, float]) -> list[str] | None:
    """Greedy separation: a minimal cover that x violates, or None if this greedy finds none.

    Items cheap to include, those with x_i near 1 per unit of weight, go in first, until the set
    overruns b; then items are dropped, worst first, while the set stays a cover.
    """
    order = sorted((i for i in a if a[i] > 0), key=lambda i: ((1 - x[i]) / a[i], i))
    cover, weight = [], 0.0
    for i in order:
        cover.append(i)
        weight += a[i]
        if weight > b:
            break
    else:
        return None
    for i in sorted(cover, key=lambda i: (-(1 - x[i]), i)):
        if is_cover([j for j in cover if j != i], a, b):
            cover.remove(i)
    return cover if violation(cover, x) > EPS else None


def lp_with_cuts(values: dict[str, float], a: dict[str, float], b: float,
                 cuts: list[list[str]]) -> tuple[float, dict[str, float]]:
    """The knapsack's LP relaxation with the cover cuts added, solved by GLOP."""
    model = mathopt.Model(name="knapsack with cuts")
    x = {i: model.add_variable(lb=0, ub=1, name=f"x_{i}") for i in values}
    model.maximize(sum(values[i] * x[i] for i in values))
    model.add_linear_constraint(sum(a[i] * x[i] for i in values) <= b, name="budget")
    for k, cover in enumerate(cuts):
        model.add_linear_constraint(sum(x[i] for i in cover) <= len(cover) - 1, name=f"cover_{k}")
    result = mathopt.solve(model, mathopt.SolverType.GLOP)
    return result.objective_value(), {i: result.variable_values(x[i]) for i in values}


def cover_rounds(values: dict[str, float], a: dict[str, float], b: float, max_rounds: int = 20):
    """Solve the LP, add the cover it violates, repeat. Yields (round, bound, fractional items, cut)."""
    cuts: list[list[str]] = []
    for k in range(max_rounds + 1):
        bound, x = lp_with_cuts(values, a, b, cuts)
        fractional = sorted(i for i in x if EPS < x[i] < 1 - EPS)
        cover = separate(a, b, x)
        yield k, bound, {i: x[i] for i in fractional}, cover
        if cover is None:
            return
        cuts.append(cover)
