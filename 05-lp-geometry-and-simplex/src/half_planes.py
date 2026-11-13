"""Each row of the budget split keeps one side of a line; the plans that keep every side are the region."""

from split_lp import BOUNDS, ROWS

ALL = {**ROWS, **BOUNDS}


def broken(d: float, t: float, rows=ALL) -> list[str]:
    """The labels of the rows a plan (d, t) breaks; an empty list means the plan is feasible."""
    return [label for label, ((a_d, a_t), b) in rows.items() if a_d * d + a_t * t > b + 1e-9]


def picture(rows=ALL, marks=None, d_max=30, t_max=22) -> list[str]:
    """A character map: '#' for a feasible grid point, '.' for one that breaks a row, a letter for a vertex."""
    marks = marks or {}
    lines = []
    for t in range(t_max, -1, -2):
        cells = "".join(marks.get((d, t)) or ("#" if not broken(d, t, rows) else ".") for d in range(d_max + 1))
        lines.append(f"t={t:2} {cells}")
    lines.append("     d=0" + " " * 7 + "d=10" + " " * 6 + "d=20" + " " * 6 + "d=30")
    return lines


if __name__ == "__main__":
    for d, t in [(10, 10), (20, 10), (5, 25), (16, 16), (12, 18)]:
        rows = broken(d, t)
        print(f"plan d={d:2}, t={t:2}:", "feasible" if not rows else "breaks " + ", ".join(rows))
    print()
    print("\n".join(picture(marks={(0, 0): "A", (24, 0): "B", (12, 18): "C", (10, 20): "D", (0, 20): "E"})))
