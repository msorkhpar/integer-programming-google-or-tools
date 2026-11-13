from __future__ import annotations


def allowed_overrun(row_size: float, unit: float, tol: float, relative: bool) -> float:
    """The largest overspend, in dollars, a check with tolerance `tol` accepts on this row."""
    # TODO: convert the row's size into its units, apply the tolerance, convert back to dollars.
    return 0.0


if __name__ == "__main__":
    print(allowed_overrun(8_720_000, 1_000, 1e-6, relative=False))
