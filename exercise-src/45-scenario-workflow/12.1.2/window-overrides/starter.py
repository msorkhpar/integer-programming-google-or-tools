from __future__ import annotations


def bounds_for(kind: str, years: tuple[int, ...], window: range) -> dict[int, tuple[int, int]] | None:
    """{start year: (lower, upper)} for one override, or None when it leaves no start year at all."""
    bounds = {}
    # TODO: one (lower, upper) pair per year of the window, for each kind of override.
    return bounds


if __name__ == "__main__":
    print(bounds_for("only_between", (2028, 2029), range(2027, 2031)))
