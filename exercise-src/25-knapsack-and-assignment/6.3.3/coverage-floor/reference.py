from __future__ import annotations

from ortools.math_opt.python import mathopt


def separate_floor(km: dict[str, int], floor: int, xstar: dict[str, float]) -> list[str] | None:
    """A set of lines the LP point under-uses although every plan meeting the floor needs one of them.

    A set C is needed when the lines outside it add up to less than the floor: then every plan that
    inspects at least `floor` km includes a line of C, so sum over C of x >= 1 holds for whole plans.
    Returns the needed set with the smallest LP sum when that sum is below 1, else None.
    """
    total = sum(km.values())
    model = mathopt.Model(name="separate-floor")
    z = {i: model.add_binary_variable(name=f"z_{i}") for i in km}           # z_i = 1: line i is in C
    # Outside C: total - sum km_i z_i <= floor - 1, since lengths are whole kilometres.
    model.add_linear_constraint(sum(km[i] * z[i] for i in km) >= total - floor + 1, name="needed")
    model.minimize(sum(xstar[i] * z[i] for i in km))
    result = mathopt.solve(model, mathopt.SolverType.HIGHS)
    if result.termination.reason != mathopt.TerminationReason.OPTIMAL:
        return None
    needed = [i for i in km if result.variable_values(z[i]) > 0.5]
    return needed if sum(xstar[i] for i in needed) < 1 - 1e-9 else None


if __name__ == "__main__":
    print(separate_floor({"L1": 10, "L2": 3, "L3": 2}, 8, {"L1": 0.5, "L2": 1.0, "L3": 1.0}))
