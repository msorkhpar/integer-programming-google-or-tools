"""What a Python float can and cannot hold, measured on GridCap-sized money."""

import math
import sys

from gridcap import generate

print(f"0.1 + 0.2 = {0.1 + 0.2!r}   equal to 0.3: {0.1 + 0.2 == 0.3}")
print(f"machine epsilon: {sys.float_info.epsilon!r}  (2**-52 = {2.0 ** -52!r})")
print("gap to the next float (math.ulp):")
for label, value in (("1", 1.0), ("a budget in $k", 8_890.0), ("the same budget in $", 8_890_000.0),
                     ("the same budget in cents", 889_000_000.0), ("1e10", 1e10), ("1e16", 1e16)):
    print(f"  {label:26} {value:>16,.0f}  ulp {math.ulp(value):.1e}")
print(f"1e16 + 1 == 1e16: {1e16 + 1 == 1e16}")

# Every project's 2027 spend in dollars, escalated by 3.1% a year from 2025: dollars with cents.
small = generate("small")
spend = [p.spend(p.earliest_start).get(2027, 0) * 1000 * 1.031 ** 2 for p in small.projects]
spend = [round(s, 2) for s in spend if s]
forward = 0.0
for s in spend:
    forward += s
backward = 0.0
for s in reversed(spend):
    backward += s
cents = sum(round(s * 100) for s in spend)
print(f"{len(spend)} amounts with cents, summed forward:  {forward!r}")
print(f"{len(spend)} amounts with cents, summed backward: {backward!r}")
print(f"math.fsum: {math.fsum(spend)!r}   integer cents: {cents} (= ${cents // 100:,}.{cents % 100:02d})")
