from __future__ import annotations

EPS = 1e-9


def reduce_row(coefs: dict[str, float], rhs: float, lo: dict[str, int],
               hi: dict[str, int]) -> tuple[str, dict[str, int]]:
    """What presolve concludes from one <= row: a verdict and the variables the row fixes."""
    least = sum(a * (lo[j] if a > 0 else hi[j]) for j, a in coefs.items())
    most = sum(a * (hi[j] if a > 0 else lo[j]) for j, a in coefs.items())
    if least > rhs + EPS:
        return "infeasible", {}
    if most <= rhs:
        return "redundant", {}
    fixings = {}
    for j, a in coefs.items():
        if lo[j] == hi[j]:
            continue
        if a > 0 and least + a > rhs + EPS:
            fixings[j] = 0
        elif a < 0 and least - a > rhs + EPS:
            fixings[j] = 1
    return "keep", fixings


if __name__ == "__main__":
    print(reduce_row({"p": 7, "q": 7, "r": 1}, 6, {"p": 0, "q": 0, "r": 0}, {"p": 1, "q": 1, "r": 1}))
