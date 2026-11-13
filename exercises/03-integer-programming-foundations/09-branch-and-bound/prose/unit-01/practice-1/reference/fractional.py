from __future__ import annotations


def fractional(x: dict[str, float], tol: float = 1e-6) -> list[str]:
    """Names whose LP value is more than tol from the nearest whole number, in the order of x."""
    return [name for name, v in x.items() if abs(v - round(v)) > tol]


if __name__ == "__main__":
    print(fractional({"open_north": 1.0, "open_south": 0.4, "trucks_north": 3.0, "trucks_south": 2.6}))
