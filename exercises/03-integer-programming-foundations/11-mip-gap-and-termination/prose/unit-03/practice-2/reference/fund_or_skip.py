from __future__ import annotations


def fund_or_skip(forced_in: tuple[float, float] | None, forced_out: tuple[float, float] | None) -> str:
    """Compare the brackets of two runs of a maximization, one with the project forced in, one forced out."""
    if forced_out is None:
        return "fund"
    if forced_in is None:
        return "skip"
    in_incumbent, in_bound = forced_in
    out_incumbent, out_bound = forced_out
    if in_incumbent > out_bound:
        return "fund"
    if out_incumbent > in_bound:
        return "skip"
    return "undecided"


if __name__ == "__main__":
    print(fund_or_skip(forced_in=(1_000, 1_010), forced_out=(980, 995)))
