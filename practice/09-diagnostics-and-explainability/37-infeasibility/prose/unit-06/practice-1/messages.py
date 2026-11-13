from __future__ import annotations


def sentence(row: str, jobs: dict, caps: dict, crews: dict) -> str:
    """One conflict row of the road program, in the words the city's planners use."""
    # TODO: one sentence per kind of row, as the table in the statement says.
    return row


def translate(conflict: list[str], jobs: dict, caps: dict, crews: dict) -> list[str]:
    return [sentence(row, jobs, caps, crews) for row in conflict]


if __name__ == "__main__":
    jobs = {"R12": "Elm Street"}
    print(translate(["need_R12", "cap_2027"], jobs, {2027: 12500}, {}))
