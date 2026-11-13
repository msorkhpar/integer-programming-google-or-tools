from __future__ import annotations


def read_footer(log: list[str]) -> dict:
    """Read the verdict of a HiGHS log: its status, its iterations by kind, and its objective.

    The objective is an answer only when the status is Optimal; otherwise it is None.
    """
    # TODO: find the "Model status", "... iterations" and "Objective value" lines.
    return {"status": None, "iterations": {"Simplex": -1}, "objective": 0.0}


if __name__ == "__main__":
    demo = ["Model name          : demo", "Model status        : Optimal", "Simplex   iterations: 3",
            "Objective value     :  1.2500000000e+02", "HiGHS run time      :          0.00"]
    print(read_footer(demo))
