from __future__ import annotations

from ortools.math_opt.python import mathopt


def fewest_refusals(vessels: dict, berths: dict) -> tuple[list[str], dict[str, int]]:
    """Refuse as few berthing requests as possible; every vessel still berths once, inside its window."""
    # TODO: write the formulation first, then build and solve it with HiGHS.
    # Return the refused vessels (sorted) and the day each vessel berths.
    return [], {v: wanted for v, (_, _, wanted) in vessels.items()}


if __name__ == "__main__":
    print(fewest_refusals({"Aurora": (1, 2, 1), "Borealis": (1, 2, 1)}, {1: 1, 2: 1}))
