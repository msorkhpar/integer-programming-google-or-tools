"""Solve GridCap small with each broken rule, and ask what a whole-model test would see.

GridCap is a fictional utility's portfolio. The whole-model test here is the usual one: solve the
full portfolio, then check that the plan breaks no rule (audit.violations) and that its value has
not changed. A bug that never changes the optimal plan passes that test.
"""

from __future__ import annotations

from gridcap import generate

from audit import violations
from bugs import BUGS, broken
from plan_model import optimize


def whole_model_test(portfolio, rules) -> tuple[float, str, str]:
    """Solve with these rules; PASS when the plan breaks no rule and its NPV is the correct one."""
    _, best, plan = optimize(portfolio)
    _, npv, got = optimize(portfolio, rules)
    same = "same plan" if got == plan else "plan changed"
    ok = not violations(portfolio, got) and abs(npv - best) < 1e-3
    return npv, same, "PASS" if ok else "FAIL"


def main() -> None:
    for size in ("tiny", "small"):
        portfolio = generate(size)
        status, best, plan = optimize(portfolio)
        print(f"GridCap {size}: correct model {status}, NPV {best:,.1f}, {len(plan)} projects")
        for name in BUGS:
            npv, same, verdict = whole_model_test(portfolio, broken(name))
            print(f"  {name:<29} NPV {npv:>9,.1f}  {same:<12}  whole-model test {verdict}")


if __name__ == "__main__":
    main()
