from __future__ import annotations


def check_runs(runs: list[dict], tol: float) -> list[str]:
    """Problems with a set of runs of one LP on several devices; an empty list means they agree.

    A run is {"device": "cpu" | "gpu", "solver": str, "objective": float, "digest": str}.
    """
    cpu = [r for r in runs if r["device"] == "cpu"]
    if not cpu:
        return ["no CPU reference"]
    reference = cpu[0]["objective"]
    problems = []
    first = {}
    for r in runs:
        key = (r["device"], r["solver"])
        if key in first and (first[key]["digest"], first[key]["objective"]) != (r["digest"], r["objective"]):
            problems.append(f"{r['device']}/{r['solver']}: repeat differs")
        first.setdefault(key, r)
        if abs(r["objective"] - reference) > tol * max(1.0, abs(reference)):
            problems.append(f"{r['device']}/{r['solver']}: off the reference")
    return sorted(set(problems))


if __name__ == "__main__":
    print(check_runs([{"device": "cpu", "solver": "ipm", "objective": 10.0, "digest": "a"}], 1e-6))
