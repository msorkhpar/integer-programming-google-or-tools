from __future__ import annotations


def fingerprint(plan: dict[str, int]) -> str:
    """16 hex characters naming the plan: the same in every process, different for different plans."""
    # TODO: write it.
    return "0" * 16


if __name__ == "__main__":
    print(fingerprint({"M07": 2028, "M12": 2027}))
