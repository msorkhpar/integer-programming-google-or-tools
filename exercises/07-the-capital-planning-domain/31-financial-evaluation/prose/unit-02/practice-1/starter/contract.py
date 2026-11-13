from __future__ import annotations


def billed(estimate: tuple[float, ...], price_year: int, start: int, escalation: float) -> dict[int, float]:
    """{calendar year: amount billed} for a job started in `start`, priced in `price_year` prices."""
    # TODO: place each year of work in its calendar year, at that year's prices.
    return {}


if __name__ == "__main__":
    print(billed((400, 250), 2026, 2028, 0.04))
