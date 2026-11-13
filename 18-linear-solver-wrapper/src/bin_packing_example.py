"""Lesson 4.7.4: the OR-Tools bin-packing example, solved by the MathOpt port of its model.

Data from bin_packing_mip.py,
https://github.com/google/or-tools/blob/stable/ortools/linear_solver/samples/bin_packing_mip.py
(Apache-2.0).
"""

from bin_packing import first_fit_decreasing, lower_bound, pack

WEIGHTS = [48, 30, 19, 36, 36, 27, 42, 42, 36, 24, 30]
CAPACITY = 100

print(f"{len(WEIGHTS)} items, total weight {sum(WEIGHTS)}, bins of {CAPACITY}: "
      f"at least {lower_bound(WEIGHTS, CAPACITY)} bins")
result, packing = pack(WEIGHTS, CAPACITY, max_bins=len(WEIGHTS))
print(f"MIP: {result.termination.reason.name}, {len(packing)} bins")
for b, items in enumerate(packing):
    print(f"  bin {b}: items {items}, weight {sum(WEIGHTS[i] for i in items)}")
ffd = first_fit_decreasing(WEIGHTS, CAPACITY)
print(f"first fit decreasing: {len(ffd)} bins")

# A small case where first fit decreasing is not optimal.
sizes, capacity = [3, 3, 2, 2, 2, 2], 7
ffd = first_fit_decreasing(sizes, capacity)
result, packing = pack(sizes, capacity, max_bins=len(ffd))
print(f"sizes {sizes}, bins of {capacity}: at least {lower_bound(sizes, capacity)}; "
      f"first fit decreasing {[[sizes[i] for i in b] for b in ffd]}; MIP {[[sizes[i] for i in b] for b in packing]}")
