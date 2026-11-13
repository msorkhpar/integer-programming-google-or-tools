from __future__ import annotations


def crew_bound(builds: dict, hours: dict[int, int], prices: dict[int, float]) -> tuple[float, dict[str, int]]:
    """L(mu) for the crew rows priced at `prices`, and the relaxed plan that reaches it."""
    # TODO: write L(mu) as a formula first, then compute it and the relaxed plan.
    return 0.0, {}


if __name__ == "__main__":
    builds = {"north ring": {"value": {2027: 50, 2028: 44}, "hours": [30, 10], "must": False}}
    print(crew_bound(builds, {2027: 40, 2028: 40}, {2027: 0.5, 2028: 0.5}))
