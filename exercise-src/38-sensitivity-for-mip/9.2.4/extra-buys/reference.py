from __future__ import annotations


def what_extra_buys(points: list[tuple[int, int]], budget: int, extra: int) -> dict | None:
    """What `extra` more buys from `budget`, read off a step curve's points."""
    if budget < points[0][0]:
        return None                                              # no plan fits this budget
    here = max(v for b, v in points if b <= budget)              # V jumps at a step's budget
    there = max(v for b, v in points if b <= budget + extra)
    crossed = [b for b, _ in points if budget < b <= budget + extra]
    above = [(b, v) for b, v in points if b > budget]
    upcoming = (above[0][0], above[0][1] - here) if above else None
    return {"gain": there - here, "steps": len(crossed), "next": upcoming}


if __name__ == "__main__":
    curve = [(100, 40), (130, 52), (150, 70), (210, 81)]
    print(what_extra_buys(curve, 120, 40))
