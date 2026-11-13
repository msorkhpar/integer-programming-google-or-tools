"""A plan is a set of project ids. Its cost and its value are sums over the projects it funds."""

from gridcap import generate

tiny = generate("tiny")


def cost(plan: set[str]) -> int:
    return sum(tiny.project(pid).capex for pid in plan)


def value(plan: set[str]) -> int:
    return sum(tiny.project(pid).value for pid in plan)


if __name__ == "__main__":
    for plan in ({"P001", "P002", "P006"}, {"P002", "P003", "P004"}):
        verdict = "within budget" if cost(plan) <= tiny.capital_budget else "over budget"
        print(sorted(plan), f"cost ${cost(plan):,}k", f"value ${value(plan):,}k", verdict)
