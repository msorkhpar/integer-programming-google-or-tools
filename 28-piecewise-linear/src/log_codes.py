"""Lesson 6.6.3: the logarithmic form's codes, and a check that its rows allow exactly one segment per code.

Each segment gets a Gray code, so neighbouring segments differ in one bit. For each bit b, the
breakpoints whose every segment has b = 1 may carry weight only when z_b = 1, and those whose every
segment has b = 0 only when z_b = 0. The program prints the sets for 4 segments, then fixes each
code for 2 to 9 segments and asks HiGHS which breakpoints may carry weight.
"""

import itertools

from ortools.math_opt.python import mathopt

from piecewise import Curve, add_log, gray, log_sets
from selection import solve_highs


def weighted(K: int, code: tuple[int, ...]) -> list[int]:
    """The breakpoints that may carry weight when the bits are fixed to `code`."""
    curve = Curve(tuple(range(K + 1)), tuple(0 for _ in range(K + 1)))
    found = []
    for j in range(K + 1):
        model = mathopt.Model()
        piece = add_log(model, curve, "c")
        for bit, v in zip(piece.binaries, code):
            bit.lower_bound = bit.upper_bound = v
        model.maximize(piece.parts["lam"][j])
        result = solve_highs(model)
        if result.termination.reason == mathopt.TerminationReason.OPTIMAL and result.objective_value() > 0.5:
            found.append(j)
    return found


if __name__ == "__main__":
    K = 4
    print("4 segments: segment s runs from breakpoint s to s+1")
    print("segment codes (bit1 bit0):", {s: format(gray(s), "02b") for s in range(K)})
    for b, (ones, zeros) in enumerate(log_sets(K)):
        print(f"bit {b}: breakpoints {ones} need z_{b} = 1, breakpoints {zeros} need z_{b} = 0")
    for code in itertools.product((0, 1), repeat=2):
        bits = code[::-1]                                     # z_0 first
        print(f"z_1 z_0 = {code[0]}{code[1]}: weight allowed on breakpoints {weighted(K, bits)}")
    print("segments | binaries | every code allows one segment's two ends, unused codes none")
    for K in range(2, 10):
        n = len(log_sets(K))
        ok = True
        used = {tuple(gray(s) >> b & 1 for b in range(n)): s for s in range(K)}
        for bits in itertools.product((0, 1), repeat=n):
            want = [used[bits], used[bits] + 1] if bits in used else []
            ok &= weighted(K, bits) == want
        print(f"{K:8} | {n:8} | {ok}")
