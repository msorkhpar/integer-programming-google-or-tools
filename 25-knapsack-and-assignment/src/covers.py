"""Cover inequalities for one knapsack row: test, shrink, extend and separate them (lesson 6.3.3).

A row is sum of weight[i] * x[i] <= capacity with binary x and whole-number weights. A cover is a set
of items whose weights add up to more than the capacity, so the row allows at most |C| - 1 of them.
"""

from __future__ import annotations

from ortools.math_opt.python import mathopt

from knapsack_models import EXACT, Row, solve_highs


def is_cover(row: Row, items: list[str]) -> bool:
    """The items cannot all be funded: together they use more than the row allows."""
    return sum(row.weight[i] for i in items) > row.capacity


def minimal(row: Row, cover: list[str], xstar: dict[str, float]) -> list[str]:
    """Drop items, lowest LP value first, while what is left is still a cover."""
    kept = list(cover)
    for i in sorted(cover, key=lambda i: xstar[i]):
        if is_cover(row, [j for j in kept if j != i]):
            kept.remove(i)
    return kept


def extension(row: Row, cover: list[str]) -> list[str]:
    """Items outside the cover that weigh at least as much as its heaviest item."""
    heaviest = max(row.weight[i] for i in cover)
    return [i for i in row.weight if i not in cover and row.weight[i] >= heaviest]


def separate(row: Row, xstar: dict[str, float]) -> tuple[list[str], float]:
    """The cover whose row the LP point breaks by the most: itself a small knapsack, solved by HiGHS.

    The cover row sum_C x_i <= |C| - 1 reads sum_C (1 - x_i) >= 1, so the most broken cover is the one
    with the least sum of (1 - x*_i). Returns the cover and that sum; the row is broken when it is below 1.
    """
    model = mathopt.Model(name=f"separate_{row.name}")
    z = {i: model.add_binary_variable(name=f"z_{i}") for i in row.weight}       # z_i = 1: i is in the cover
    model.add_linear_constraint(sum(w * z[i] for i, w in row.weight.items()) >= row.capacity + 1,
                                name="is_a_cover")
    model.minimize(sum((1 - xstar[i]) * z[i] for i in row.weight))
    result = solve_highs(model, EXACT)
    if result.termination.reason != mathopt.TerminationReason.OPTIMAL:
        return [], float("inf")                       # the items together fit: the row has no cover
    return [i for i in row.weight if result.variable_values(z[i]) > 0.5], result.objective_value()
