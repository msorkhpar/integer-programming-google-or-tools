from __future__ import annotations


def fund_or_skip(forced_in: tuple[float, float] | None, forced_out: tuple[float, float] | None) -> str:
    """Compare the brackets of two runs of a maximization, one with the project forced in, one forced out."""
    # TODO: compare each run's incumbent with the other run's bound.
    return "?"


if __name__ == "__main__":
    print(fund_or_skip(forced_in=(1_000, 1_010), forced_out=(980, 995)))
