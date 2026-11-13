from __future__ import annotations


def cs_violations(value: dict[str, float], rows: dict[str, tuple[dict[str, float], str, float]],
                  plan: dict[str, float], prices: dict[str, float], tol: float = 1e-6) -> list[str]:
    """The rows and activities where the plan and the prices break complementary slackness, sorted."""
    broken = []
    for name, (coeffs, sense, rhs) in rows.items():
        used = sum(c * plan[a] for a, c in coeffs.items())
        slack = rhs - used if sense == "<=" else used - rhs
        if slack > tol and abs(prices[name]) > tol:
            broken.append(name)
    for activity, worth in value.items():
        reduced = worth - sum(coeffs.get(activity, 0) * prices[name] for name, (coeffs, _, _) in rows.items())
        if plan[activity] > tol and abs(reduced) > tol:
            broken.append(activity)
    return sorted(broken)


if __name__ == "__main__":
    value = {"inspect": 4, "repair": 3}
    rows = {"hours": ({"inspect": 1, "repair": 1}, "<=", 10), "inspect_cap": ({"inspect": 1}, "<=", 6)}
    print(cs_violations(value, rows, {"inspect": 6, "repair": 4}, {"hours": 3, "inspect_cap": 1}))
    print(cs_violations(value, rows, {"inspect": 5, "repair": 4}, {"hours": 3, "inspect_cap": 1}))
