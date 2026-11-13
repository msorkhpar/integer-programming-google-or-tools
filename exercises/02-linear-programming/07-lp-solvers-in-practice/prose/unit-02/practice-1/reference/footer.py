from __future__ import annotations


def read_footer(log: list[str]) -> dict:
    """Read the verdict of a HiGHS log: its status, its iterations by kind, and its objective.

    The objective is an answer only when the status is Optimal; otherwise it is None.
    """
    status = None
    iterations: dict[str, int] = {}
    objective = None
    for line in log:
        if ":" not in line:
            continue
        key, value = (part.strip() for part in line.split(":", 1))
        if key == "Model status":
            status = value
        elif key.endswith("iterations"):
            iterations[key.split()[0]] = int(value)
        elif key == "Objective value":
            objective = float(value)
    if status != "Optimal":
        objective = None
    return {"status": status, "iterations": iterations, "objective": objective}


if __name__ == "__main__":
    demo = ["Model name          : demo", "Model status        : Optimal", "Simplex   iterations: 3",
            "Objective value     :  1.2500000000e+02", "HiGHS run time      :          0.00"]
    print(read_footer(demo))
