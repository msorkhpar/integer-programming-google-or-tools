from __future__ import annotations

#: The swing of each measure, fixed by the board before any project is scored: from no benefit (0)
#: to this much. NPV and risk in $k, minutes in customer-minutes of outage avoided.
REFERENCE = {"npv": 500.0, "risk": 200.0, "minutes": 100_000.0}
#: The board's swing ratings: the biggest swing gets 100.
RATINGS = {"risk": 100, "minutes": 80, "npv": 60}


def weights(ratings: dict[str, float]) -> dict[str, float]:
    """Each rating over the total, so the weights sum to 1."""
    # TODO: see the lesson "Weights, swing weighting and stakeholder buy-in"
    return {k: 0.0 for k in ratings}


def value_table(measures: dict[str, dict], reference: dict[str, float] = REFERENCE,
                ratings: dict[str, float] = RATINGS) -> dict[tuple[str, int], float]:
    """v[i, t] = sum over measures k of w_k * m[k][i, t] / reference[k], rounded to 6 decimals."""
    # TODO: one value per (project, start) found in any measure's table; a missing entry counts 0.
    return {}


def ranking(table: dict[tuple[str, int], float]) -> list[tuple[str, int]]:
    """Every start, highest value first; equal values in key order."""
    # TODO
    return []


if __name__ == "__main__":
    measures = {"npv": {("J1", 2027): 250}, "risk": {("J1", 2027): 100}, "minutes": {("J1", 2027): 0}}
    print(value_table(measures))
