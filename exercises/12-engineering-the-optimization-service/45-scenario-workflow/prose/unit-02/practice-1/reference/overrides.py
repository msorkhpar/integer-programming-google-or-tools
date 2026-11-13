from __future__ import annotations


def bounds_for(kind: str, years: tuple[int, ...], window: range) -> dict[int, tuple[int, int]] | None:
    """{start year: (lower, upper)} for one override, or None when it leaves no start year at all."""
    bounds = {}
    for t in window:
        if kind == "start_in":
            bounds[t] = (1, 1) if t == years[0] else (0, 0)
        elif kind == "only_between":
            bounds[t] = (0, 1) if years[0] <= t <= years[1] else (0, 0)
        elif kind == "skip_years":
            bounds[t] = (0, 0) if t in years else (0, 1)
        else:
            bounds[t] = (0, 1)
    if all(b == (0, 0) for b in bounds.values()):
        return None
    return bounds


if __name__ == "__main__":
    print(bounds_for("only_between", (2028, 2029), range(2027, 2031)))
