"""Module 28's piecewise-linear toolkit: a curve given by its breakpoints, and the formulations that put it in a MathOpt model.

A `Curve` is a list of breakpoints (x_0, y_0), ..., (x_K, y_K) with x_0 < x_1 < ... < x_K; between
two neighbours the function is the straight line joining them. Each `add_*` function adds one
formulation of "y = f(x)" to a model and returns a `Piece`: the expressions x and y, which the
caller puts into its budget row or objective, and the binaries the formulation needed.

- `add_segments` and `add_epigraph` (lesson 6.6.1): no binaries; exact only for a convex cost the
  solver wants small, or a concave value it wants large.
- `add_lambda` (lesson 6.6.2): weights on the breakpoints, with one binary per segment to keep the
  weights on two neighbours (the SOS2 rule). `binaries=False` drops them.
- `add_incremental` and `add_log` (lesson 6.6.3): the incremental (delta) form, and the lambda
  weights with a logarithmic number of binaries.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field

from ortools.math_opt.python import mathopt


@dataclass(frozen=True)
class Curve:
    xs: tuple[float, ...]
    ys: tuple[float, ...]

    def slopes(self) -> list[float]:
        return [(self.ys[k + 1] - self.ys[k]) / (self.xs[k + 1] - self.xs[k]) for k in range(len(self.xs) - 1)]

    def __call__(self, x: float) -> float:
        """The curve's value at x, interpolated between the two breakpoints around it."""
        for k in range(len(self.xs) - 1):
            if self.xs[k] <= x <= self.xs[k + 1]:
                return self.ys[k] + self.slopes()[k] * (x - self.xs[k])
        raise ValueError(f"{x} is outside [{self.xs[0]}, {self.xs[-1]}]")

    def convex(self) -> bool:
        s = self.slopes()
        return all(a <= b + 1e-9 for a, b in zip(s, s[1:]))

    def concave(self) -> bool:
        s = self.slopes()
        return all(a >= b - 1e-9 for a, b in zip(s, s[1:]))


@dataclass
class Piece:
    x: mathopt.LinearExpression
    y: mathopt.LinearExpression
    binaries: list[mathopt.Variable] = field(default_factory=list)
    parts: dict = field(default_factory=dict)       # the formulation's own variables, by role


def add_segments(model: mathopt.Model, curve: Curve, name: str) -> Piece:
    """y = f(x) for a convex f the solver wants small: one bounded variable per segment."""
    s = curve.slopes()
    delta = [model.add_variable(lb=0, ub=curve.xs[k + 1] - curve.xs[k], name=f"{name}_d{k}")
             for k in range(len(s))]
    x = curve.xs[0] + sum(delta)
    y = curve.ys[0] + sum(s[k] * delta[k] for k in range(len(s)))
    return Piece(x, y, parts={"delta": delta})


def add_epigraph(model: mathopt.Model, curve: Curve, name: str) -> Piece:
    """y >= f(x) as one row per segment's line; exact for a convex f the solver wants small."""
    x = model.add_variable(lb=curve.xs[0], ub=curve.xs[-1], name=f"{name}_x")
    y = model.add_variable(lb=-math.inf, name=f"{name}_y")
    for k, slope in enumerate(curve.slopes()):
        model.add_linear_constraint(y >= curve.ys[k] + slope * (x - curve.xs[k]), name=f"{name}_line{k}")
    return Piece(x, y)


def add_lambda(model: mathopt.Model, curve: Curve, name: str, *, binaries: bool = True) -> Piece:
    """y = f(x) for any f: weights on the breakpoints, nonzero on two neighbours only."""
    n = len(curve.xs)
    lam = [model.add_variable(lb=0, ub=1, name=f"{name}_lam{j}") for j in range(n)]
    model.add_linear_constraint(sum(lam) == 1, name=f"{name}_weights")
    seg = []
    if binaries:
        seg = [model.add_binary_variable(name=f"{name}_seg{k}") for k in range(n - 1)]
        model.add_linear_constraint(sum(seg) == 1, name=f"{name}_one_segment")
        for j in range(n):
            touching = [seg[k] for k in (j - 1, j) if 0 <= k < n - 1]
            model.add_linear_constraint(lam[j] <= sum(touching), name=f"{name}_near{j}")
    x = sum(curve.xs[j] * lam[j] for j in range(n))
    y = sum(curve.ys[j] * lam[j] for j in range(n))
    return Piece(x, y, seg, {"lam": lam})


def add_incremental(model: mathopt.Model, curve: Curve, name: str) -> Piece:
    """y = f(x) for any f: segments filled in order, a binary saying each one is full."""
    K = len(curve.xs) - 1
    fill = [model.add_variable(lb=0, ub=1, name=f"{name}_fill{k}") for k in range(K)]
    full = [model.add_binary_variable(name=f"{name}_full{k}") for k in range(K - 1)]
    for k in range(K - 1):
        model.add_linear_constraint(fill[k + 1] <= full[k], name=f"{name}_next{k}")
        model.add_linear_constraint(full[k] <= fill[k], name=f"{name}_full{k}")
    x = curve.xs[0] + sum((curve.xs[k + 1] - curve.xs[k]) * fill[k] for k in range(K))
    y = curve.ys[0] + sum((curve.ys[k + 1] - curve.ys[k]) * fill[k] for k in range(K))
    return Piece(x, y, full, {"fill": fill})


def gray(s: int) -> int:
    """The s-th Gray code: neighbours differ in exactly one bit."""
    return s ^ (s >> 1)


def log_sets(K: int) -> list[tuple[list[int], list[int]]]:
    """For each bit b: the breakpoints that need bit b = 1, and those that need it = 0."""
    bits = max(1, math.ceil(math.log2(K)))
    code = [gray(s) for s in range(K)]
    near = [[s for s in (j - 1, j) if 0 <= s < K] for j in range(K + 1)]
    return [([j for j in range(K + 1) if all(code[s] >> b & 1 for s in near[j])],
             [j for j in range(K + 1) if all(not code[s] >> b & 1 for s in near[j])])
            for b in range(bits)]


def add_log(model: mathopt.Model, curve: Curve, name: str) -> Piece:
    """y = f(x) for any f: lambda weights kept on two neighbours by ceil(log2 K) binaries."""
    n = len(curve.xs)
    lam = [model.add_variable(lb=0, ub=1, name=f"{name}_lam{j}") for j in range(n)]
    model.add_linear_constraint(sum(lam) == 1, name=f"{name}_weights")
    z = []
    for b, (ones, zeros) in enumerate(log_sets(n - 1)):
        z.append(model.add_binary_variable(name=f"{name}_bit{b}"))
        model.add_linear_constraint(sum(lam[j] for j in ones) <= z[b], name=f"{name}_one{b}")
        model.add_linear_constraint(sum(lam[j] for j in zeros) <= 1 - z[b], name=f"{name}_zero{b}")
    x = sum(curve.xs[j] * lam[j] for j in range(n))
    y = sum(curve.ys[j] * lam[j] for j in range(n))
    return Piece(x, y, z, {"lam": lam})


def value(result: mathopt.SolveResult, expr) -> float:
    """The value of a variable or a linear expression in a solution."""
    return mathopt.evaluate_expression(expr + 0, result.variable_values())


FORMS = {"lambda": add_lambda, "incremental": add_incremental, "log": add_log}
