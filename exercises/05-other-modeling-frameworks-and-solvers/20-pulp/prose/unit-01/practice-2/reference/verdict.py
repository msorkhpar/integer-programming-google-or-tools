from __future__ import annotations

import pulp


def report(prob: pulp.LpProblem) -> tuple[str, float | None]:
    """After prob.solve(...): ("proved", value), ("unproved", value) or ("no plan", None)."""
    if prob.status != pulp.LpStatusOptimal:
        return "no plan", None
    verdict = "proved" if prob.sol_status == pulp.LpSolutionOptimal else "unproved"
    return verdict, pulp.value(prob.objective)


if __name__ == "__main__":
    demo = pulp.LpProblem("demo", pulp.LpMaximize)
    a = demo.add_variable("a", 0, 1, cat=pulp.LpBinary)
    b = demo.add_variable("b", 0, 1, cat=pulp.LpBinary)
    demo += 3 * a + 2 * b, "value"
    demo += a + b <= 1, "one"
    demo.solve(pulp.PULP_CBC_CMD(msg=False))
    print(report(demo))
