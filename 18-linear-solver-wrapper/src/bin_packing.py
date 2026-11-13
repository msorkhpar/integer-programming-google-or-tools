"""Lesson 4.7.4: the bin-packing model in MathOpt, and a first-fit-decreasing packing to compare with.

The model is the one of the OR-Tools bin-packing guide (bin_packing_mip.py,
https://github.com/google/or-tools/blob/stable/ortools/linear_solver/samples/bin_packing_mip.py,
Apache-2.0), ported from pywraplp to MathOpt as in lesson 4.7.2, with one row added that orders
the bins.
"""

from __future__ import annotations

import ctypes
import math
import os
import sys

from ortools.math_opt.python import mathopt


def first_fit_decreasing(sizes: list[int], capacity: int) -> list[list[int]]:
    """Largest item first, each into the first open bin with room, else into a new bin."""
    bins: list[list[int]] = []
    room: list[int] = []
    for i in sorted(range(len(sizes)), key=lambda i: -sizes[i]):
        for b in range(len(bins)):
            if sizes[i] <= room[b]:
                bins[b].append(i)
                room[b] -= sizes[i]
                break
        else:
            bins.append([i])
            room.append(capacity - sizes[i])
    return bins


def pack(sizes: list[int], capacity: int, max_bins: int) -> tuple[mathopt.SolveResult, list[list[int]]]:
    """Fewest bins of `capacity` holding every item; at most `max_bins` bins are offered."""
    model = mathopt.Model(name="bin packing")
    items, bins = range(len(sizes)), range(max_bins)
    x = {(i, b): model.add_binary_variable(name=f"x_{i}_{b}") for i in items for b in bins}
    y = {b: model.add_binary_variable(name=f"y_{b}") for b in bins}
    for i in items:
        model.add_linear_constraint(sum(x[i, b] for b in bins) == 1, name=f"once_{i}")
    for b in bins:
        model.add_linear_constraint(sum(sizes[i] * x[i, b] for i in items) <= capacity * y[b], name=f"cap_{b}")
    for b in bins[1:]:
        model.add_linear_constraint(y[b] <= y[b - 1], name=f"order_{b}")     # use bin b only after bin b-1
    model.minimize(sum(y.values()))
    sys.stdout.flush()
    saved, sink = os.dup(1), os.open(os.devnull, os.O_WRONLY)
    os.dup2(sink, 1)                       # keep the bundled HiGHS's stray lines out of the output
    try:
        result = mathopt.solve(model, mathopt.SolverType.HIGHS)
    finally:
        ctypes.CDLL(None).fflush(None)
        os.dup2(saved, 1)
        os.close(saved)
        os.close(sink)
    packing = [[i for i in items if result.variable_values(x[i, b]) > 0.5] for b in bins]
    return result, [contents for contents in packing if contents]


def lower_bound(sizes: list[int], capacity: int) -> int:
    return math.ceil(sum(sizes) / capacity)
