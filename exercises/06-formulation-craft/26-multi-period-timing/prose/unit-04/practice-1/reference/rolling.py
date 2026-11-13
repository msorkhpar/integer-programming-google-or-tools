from __future__ import annotations

from ortools.math_opt.python import mathopt


def add_plan_cap(model: mathopt.Model, spend: dict, years: list[int], cap: int) -> None:
    """The old rule: the whole plan's spend within one cap."""
    model.add_linear_constraint(sum(spend[y] for y in years) <= cap, name="plan_cap")


def add_rolling_caps(model: mathopt.Model, spend: dict, years: list[int], k: int, cap: int) -> dict:
    """Hold the spend of every `k` consecutive years of the plan to `cap`."""
    rows = {}
    for i in range(len(years) - k + 1):
        window = years[i:i + k]
        rows[window[0]] = model.add_linear_constraint(
            sum(spend[y] for y in window) <= cap, name=f"rolling_{window[0]}")
    return rows


if __name__ == "__main__":
    model = mathopt.Model()
    x = model.add_binary_variable(name="dredging")
    spend = {2027: 50 * x, 2028: 50 * x, 2029: 0 * x}
    print(add_rolling_caps(model, spend, [2027, 2028, 2029], 2, 80))
