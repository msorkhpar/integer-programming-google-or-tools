"""Check a start-year NPV formula borrowed from interview-prep notes before using it.

The formula, with years numbered 1..T, escalation e and discount rate r:
    NPV[i, t] = sum over tau = t..T of CF[i, tau] * (1 + e) ** (tau - 1) / (1 + r) ** tau
Read literally, CF[i, tau] is indexed by calendar year and does not depend on the start t.
"""

T, r = 5, 0.07
profile = (360, 720, 1470)                  # P022's costs in its first, second and third year of work


def literal(cf: dict[int, float], t: int, e: float) -> float:
    return sum(cf.get(tau, 0) * (1 + e) ** (tau - 1) / (1 + r) ** tau for tau in range(t, T + 1))


def shifted(t: int, e: float) -> float:
    """The cost profile moved to start in year t, same exponents as the borrowed formula."""
    return sum(c * (1 + e) ** (t + k - 1) / (1 + r) ** (t + k) for k, c in enumerate(profile))


cf = {1 + k: c for k, c in enumerate(profile)}  # the profile written once, as if started in year 1
print("start  literal   shifted   (PV of cost, e = 3%)")
for t in (1, 2, 3):
    print(f"{t:>5}  {literal(cf, t, 0.03):>7.1f}   {shifted(t, 0.03):>7.1f}")

print(f"e = r, start 1: shifted {shifted(1, r):.2f}, undiscounted cost {sum(profile)}, "
      f"cost / (1 + r) {sum(profile) / (1 + r):.2f}")
