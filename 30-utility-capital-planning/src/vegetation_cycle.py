"""Lesson 7.1.2: vegetation work comes back on a cycle, so each year's work is set by earlier years.

The circuits, their miles and the four-year cycle are invented for the lesson (GridCap has no trim
history); no real utility's program is described.
"""

CYCLE = 4
YEARS = range(2027, 2035)
#: circuit -> (overhead miles, year last trimmed)
CIRCUITS = {
    "C01": (42, 2023), "C02": (35, 2023), "C03": (28, 2024), "C04": (51, 2024),
    "C05": (30, 2025), "C06": (44, 2025), "C07": (38, 2026), "C08": (26, 2026),
}


def due_miles(last_trim: dict[str, int]) -> dict[int, int]:
    """Miles due in each year if every circuit is trimmed exactly when its cycle comes round."""
    due = {y: 0 for y in YEARS}
    for c, (miles, last) in CIRCUITS.items():
        year = last_trim[c] + CYCLE
        while year in due:
            due[year] += miles
            year += CYCLE
    return due


on_time = {c: last for c, (_, last) in CIRCUITS.items()}
print(f"cycle {CYCLE} years; miles due each year when every trim is on time:")
print("  " + "  ".join(f"{y}: {m:3}" for y, m in due_miles(on_time).items()))

# 2028's work (C03 and C04, last trimmed 2024) slips to 2029.
slipped = {**on_time, "C03": 2025, "C04": 2025}
print("2028 work deferred one year; miles due each year:")
print("  " + "  ".join(f"{y}: {m:3}" for y, m in due_miles(slipped).items()))
