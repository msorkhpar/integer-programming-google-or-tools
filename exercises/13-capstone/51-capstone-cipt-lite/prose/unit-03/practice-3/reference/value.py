from __future__ import annotations

#: The swing of each measure, fixed by the board before any project is scored: from no benefit (0)
#: to this much. NPV and risk in $k, minutes in customer-minutes of outage avoided.
REFERENCE = {"npv": 500.0, "risk": 200.0, "minutes": 100_000.0}
#: The board's swing ratings: the biggest swing gets 100.
RATINGS = {"risk": 100, "minutes": 80, "npv": 60}


def weights(ratings: dict[str, float]) -> dict[str, float]:
    """Each rating over the total, so the weights sum to 1."""
    total = sum(ratings.values())
    return {k: r / total for k, r in ratings.items()}


def value_table(measures: dict[str, dict], reference: dict[str, float] = REFERENCE,
                ratings: dict[str, float] = RATINGS) -> dict[tuple[str, int], float]:
    """v[i, t] = sum over measures k of w_k * m[k][i, t] / reference[k], rounded to 6 decimals."""
    w = weights(ratings)
    keys = sorted({key for table in measures.values() for key in table})
    return {key: round(sum(w[k] * measures[k].get(key, 0.0) / reference[k] for k in measures), 6)
            for key in keys}


def ranking(table: dict[tuple[str, int], float]) -> list[tuple[str, int]]:
    """Every start, highest value first; equal values in key order."""
    return sorted(table, key=lambda key: (-table[key], key))


if __name__ == "__main__":
    measures = {"npv": {("J1", 2027): 250}, "risk": {("J1", 2027): 100}, "minutes": {("J1", 2027): 0}}
    print(value_table(measures))
