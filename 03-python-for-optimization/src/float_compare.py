"""Two correct formulas for one present value disagree in the last digit; a tolerance settles it."""

import math

from pytest import approx

from gridcap import generate

tiny = generate("tiny")
rate, base = tiny.discount_rate, tiny.years[0]
p001 = tiny.project("P001")


def pv_divide(profile: tuple[int, ...], start: int) -> float:
    return sum(c / (1 + rate) ** (start + k - base) for k, c in enumerate(profile))


def pv_multiply(profile: tuple[int, ...], start: int) -> float:
    return sum(c * (1 + rate) ** -(start + k - base) for k, c in enumerate(profile))


a = pv_divide(p001.cost_profile, p001.earliest_start)
b = pv_multiply(p001.cost_profile, p001.earliest_start)
print("divide:  ", repr(a))
print("multiply:", repr(b))
print("a == b:", a == b)
print("math.isclose(a, b):", math.isclose(a, b))
print("a == approx(b):", a == approx(b))
print()
print("approx(b) means", repr(approx(b)))
print("approx(0.0) means", repr(approx(0.0)))
print("1e-9 == approx(0.0):", 1e-9 == approx(0.0))
print("1e-9 == approx(0.0, abs=1e-6):", 1e-9 == approx(0.0, abs=1e-6))
print()
near = 0.125
print("rounded to cents:", round(near + 1e-12, 2), round(near - 1e-12, 2))
