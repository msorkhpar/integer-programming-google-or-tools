from __future__ import annotations


def forecast(objval: float, pi: float, rhs: float, low: float, up: float, new_rhs: float) -> float | None:
    """The objective at new_rhs if the current basis stays optimal there, else None."""
    if not low <= new_rhs <= up:
        return None
    return objval + pi * (new_rhs - rhs)


if __name__ == "__main__":
    print(forecast(1000.0, 2.0, 50.0, 40.0, 70.0, 60.0))
