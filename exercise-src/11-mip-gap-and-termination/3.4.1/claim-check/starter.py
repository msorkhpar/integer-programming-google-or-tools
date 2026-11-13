from __future__ import annotations


def judge_claim(value: float, incumbent: float | None, bound: float, maximize: bool) -> str:
    """Is a plan at least as good as `value` already found, still possible, or ruled out by the bound?"""
    # TODO: compare the claim with the incumbent and the bound, in the direction the objective runs.
    return "unknown"


if __name__ == "__main__":
    for claim in (5_000, 5_200, 5_400):
        print(claim, judge_claim(claim, incumbent=5_100, bound=5_300, maximize=True))
