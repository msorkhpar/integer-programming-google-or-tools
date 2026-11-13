from __future__ import annotations


def usable(use: str, gpu: dict, cpu: dict) -> tuple[bool, object]:
    """May a GPU answer serve this use of a maximisation model? Returns (accepted, value or reason).

    use "bound": gpu {"status", "objective"} from an LP relaxation; cpu {"objective"} from a CPU solve.
    use "start": gpu {"status", "x"} from a MILP; cpu {"feasible", "integral"} from the CPU check of x.
    use "plan": the plan of record.
    """
    # TODO: a plan never; a bound only optimal and confirmed; a start only if the CPU check passed.
    return False, ""


if __name__ == "__main__":
    print(usable("bound", {"status": "Optimal", "objective": 10.0}, {"objective": 10.0}))
