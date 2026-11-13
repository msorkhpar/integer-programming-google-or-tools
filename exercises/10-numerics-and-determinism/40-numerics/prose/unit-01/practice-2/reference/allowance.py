from __future__ import annotations


def allowed_overrun(row_size: float, unit: float, tol: float, relative: bool) -> float:
    """The largest overspend, in dollars, a check with tolerance `tol` accepts on this row."""
    size_in_units = abs(row_size) / unit
    allowed_in_units = tol * max(1.0, size_in_units) if relative else tol
    return allowed_in_units * unit


if __name__ == "__main__":
    print(allowed_overrun(8_720_000, 1_000, 1e-6, relative=False))
