"""Lesson 14.1.8: what the code became, step by step: lines of code and functions per package file in
every snapshot, and the tests that guard it."""

from snapshots import longest_function, size, ids_of_tests, lines_of_tests

steps = range(0, 9)
sizes = {step: size(step) for step in steps}
files = sorted({name for s in sizes.values() for name in s})
print("lines of code per file (blank lines and comments left out), steps/00 to steps/08:")
print(f"  {'':<12}" + "".join(f"{step:>6}" for step in steps))
for name in files:
    print(f"  {name:<12}" + "".join(f"{sizes[s].get(name, (0, 0))[0] or '-':>6}" for s in steps))
print(f"  {'package':<12}" + "".join(f"{sum(v[0] for v in sizes[s].values()):>6}" for s in steps))
print(f"  {'functions':<12}" + "".join(f"{sum(v[1] for v in sizes[s].values()):>6}" for s in steps))
print(f"  {'test lines':<12}" + "".join(f"{lines_of_tests(s):>6}" for s in steps))
print(f"  {'tests':<12}" + "".join(f"{len(ids_of_tests(s)):>6}" for s in steps))

print("longest function in each snapshot (lines, docstring included):")
for step in steps:
    name, length = longest_function(step)
    print(f"  steps/{step:02d}  {length:>3}  {name}")
