from __future__ import annotations


def _cap(args, jobs, caps, crews):
    return f"The {args[0]} resurfacing budget is ${caps[int(args[0])]:,}k."


def _need(args, jobs, caps, crews):
    return f"{args[0]} {jobs[args[0]]} must be done this plan."


def _pin(args, jobs, caps, crews):
    return f"Council fixed {args[0]} {jobs[args[0]]} to {args[1]}."


def _crew(args, jobs, caps, crews):
    *district, year = args                                  # a district name may hold underscores
    count = crews['_'.join(district), int(year)]
    return f"The {' '.join(district)} district has {count} paving crew{'s' if count != 1 else ''} in {year}."


def _before(args, jobs, caps, crews):
    return f"{args[0]} {jobs[args[0]]} must finish before {args[1]} {jobs[args[1]]} starts."


WRITERS = {"cap": _cap, "need": _need, "pin": _pin, "crew": _crew, "before": _before}


def unknown(row: str) -> str:
    return f"Rule {row} has no description yet."


def sentence(row: str, jobs: dict, caps: dict, crews: dict) -> str:
    """One conflict row of the road program, in the words the city's planners use."""
    kind, *args = row.split("_")
    if kind not in WRITERS:
        return unknown(row)
    try:
        return WRITERS[kind](args, jobs, caps, crews)
    except KeyError:                                        # a job, year or district the data lacks
        return unknown(row)


def translate(conflict: list[str], jobs: dict, caps: dict, crews: dict) -> list[str]:
    return [sentence(row, jobs, caps, crews) for row in conflict]


if __name__ == "__main__":
    jobs = {"R12": "Elm Street"}
    print(translate(["need_R12", "cap_2027"], jobs, {2027: 12500}, {}))
