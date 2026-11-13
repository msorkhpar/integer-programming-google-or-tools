from __future__ import annotations


def what_extra_buys(points: list[tuple[int, int]], budget: int, extra: int) -> dict | None:
    """What `extra` more buys from `budget`, read off a step curve's points."""
    # TODO: decide what a budget exactly at a step point is worth, then answer.
    return {"gain": 0, "steps": 0, "next": None}


if __name__ == "__main__":
    curve = [(100, 40), (130, 52), (150, 70), (210, 81)]
    print(what_extra_buys(curve, 120, 40))
