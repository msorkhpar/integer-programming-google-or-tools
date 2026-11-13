from __future__ import annotations


def usable(use: str, gpu: dict, cpu: dict) -> tuple[bool, object]:
    """May a GPU answer serve this use of a maximisation model? Returns (accepted, value or reason).

    use "bound": gpu {"status", "objective"} from an LP relaxation; cpu {"objective"} from a CPU solve.
    use "start": gpu {"status", "x"} from a MILP; cpu {"feasible", "integral"} from the CPU check of x.
    use "plan": the plan of record.
    """
    match use:
        case "plan":
            return False, "the plan of record runs on the CPU"
        case "bound":
            if gpu["status"] != "Optimal":
                return False, "not optimal"
            if abs(gpu["objective"] - cpu["objective"]) > 1e-6 * max(1.0, abs(cpu["objective"])):
                return False, "not confirmed"
            return True, max(gpu["objective"], cpu["objective"])
        case "start":
            if cpu["feasible"] and cpu["integral"]:
                return True, gpu["x"]
            return False, "fails the check"
    return False, "unknown use"


if __name__ == "__main__":
    print(usable("bound", {"status": "Optimal", "objective": 10.0}, {"objective": 10.0}))
