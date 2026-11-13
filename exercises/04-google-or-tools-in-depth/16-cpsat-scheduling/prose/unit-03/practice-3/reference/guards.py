from __future__ import annotations

from ortools.sat.python import cp_model


def plan_nights(guards: list[str], need: list[dict[int, int]], cost: list[list[int]],
                forbidden: list[tuple[int, int]]) -> tuple[int, dict[tuple[str, int], int]]:
    """(total move cost, (guard, night) -> place) of the cheapest roster."""
    n, nights = len(cost), range(len(need))
    flat = [cost[p][q] for p in range(n) for q in range(n)]
    model = cp_model.CpModel()
    there, at, moves = {}, {}, []
    for g in guards:
        for d in nights:
            for p in range(n):
                there[g, d, p] = model.new_bool_var(f"{g}_{d}_{p}")
            model.add_exactly_one(there[g, d, p] for p in range(n))
            at[g, d] = model.new_int_var(0, n - 1, f"at_{g}_{d}")
            model.add(at[g, d] == sum(p * there[g, d, p] for p in range(n)))
    for d in nights:
        for p in range(n - 1):
            model.add(sum(there[g, d, p] for g in guards) == need[d].get(p, 0))
    for g in guards:
        for d in nights[:-1]:
            if forbidden:
                model.add_forbidden_assignments([at[g, d], at[g, d + 1]], forbidden)
            move = model.new_int_var(0, max(flat), f"move_{g}_{d}")
            model.add_element(n * at[g, d] + at[g, d + 1], flat, move)
            moves.append(move)
    model.minimize(sum(moves))
    solver = cp_model.CpSolver()
    solver.parameters.num_workers = 1
    solver.solve(model)
    return round(solver.objective_value), {key: solver.value(v) for key, v in at.items()}


if __name__ == "__main__":
    print(plan_nights(["ana", "ben"], [{0: 1, 1: 1}, {0: 1}, {1: 2}],
                      [[0, 3, 1], [3, 0, 1], [1, 1, 0]], [(0, 1)]))
