"""Solve one model with NVIDIA cuOpt, under cuOpt's own interpreter, in its own environment.

    run_cuopt("cuopt_worker.py", "job.json")       # from lps.cuopt; prints one JSON line

The job file holds the module's model dict (see lps.py), the LP `method` ("pdlp" or "concurrent"),
extra cuOpt `settings`, whether to return the solution vector, and which log lines to keep. cuOpt's log
goes to a file, never the console: its header names the card's UUID, the CPU model and the RAM in use,
so only lines that contain a requested phrase, and none of those, are returned.
Run with no job, it says what it is and stops.
"""

from __future__ import annotations

import hashlib
import json
import os
import struct
import sys
import tempfile
import time

PRIVATE = ("UUID", "CPU:", "RAM", "host arch", "git hash")


def solve(job: dict) -> dict:
    import numpy as np
    from cuopt.linear_programming import DataModel, Solve, SolverSettings
    from cuopt.linear_programming.solver_settings import SolverMethod

    m = job["model"]
    d = DataModel()
    d.set_csr_constraint_matrix(np.array(m["values"], dtype=np.float64), np.array(m["indices"], dtype=np.int32),
                                np.array(m["offsets"], dtype=np.int32))
    d.set_constraint_lower_bounds(np.array(m["row_lb"], dtype=np.float64))
    d.set_constraint_upper_bounds(np.array(m["row_ub"], dtype=np.float64))
    d.set_objective_coefficients(np.array(m["c"], dtype=np.float64))
    d.set_variable_lower_bounds(np.array(m["lb"], dtype=np.float64))
    d.set_variable_upper_bounds(np.array(m["ub"], dtype=np.float64))
    d.set_variable_types(np.array(["I" if i else "C" for i in m["integer"]]))
    d.set_maximize(m["maximize"])
    s = SolverSettings()
    milp = any(m["integer"])
    if not milp:
        s.set_parameter("method", {"pdlp": SolverMethod.PDLP, "concurrent": SolverMethod.Concurrent}[job["method"]])
    for key, value in job["settings"].items():
        s.set_parameter(key, value)
    log = os.path.join(tempfile.mkdtemp(), "cuopt.log")
    s.set_parameter("log_to_console", False)
    s.set_parameter("log_file", log)
    start = time.perf_counter()
    sol = Solve(d, s)
    seconds = time.perf_counter() - start
    x = np.array(sol.get_primal_solution(), dtype=np.float64)
    a = np.zeros(len(m["row_lb"]))
    rows = np.repeat(np.arange(len(m["row_lb"])), np.diff(np.array(m["offsets"])))
    np.add.at(a, rows, np.array(m["values"]) * x[np.array(m["indices"], dtype=np.int64)])
    worst = max(0.0, float(np.max(np.array(m["row_lb"]) - a, initial=0.0)), float(np.max(a - np.array(m["row_ub"]), initial=0.0)),
                float(np.max(np.array(m["lb"]) - x, initial=0.0)), float(np.max(x - np.array(m["ub"]), initial=0.0)))
    out = {"solver": "cuopt-milp" if milp else f"cuopt-{job['method']}", "status": str(sol.get_termination_reason()),
           "objective": float(sol.get_primal_objective()), "seconds": seconds,
           "solver_seconds": float(sol.get_solve_time()), "violation": worst,
           "digest": hashlib.sha256(struct.pack(f"<{len(x)}d", *x)).hexdigest()[:16]}
    if milp:
        stats = sol.get_milp_stats()
        out.update(gap=float(stats["mip_gap"]), bound=float(stats["solution_bound"]), nodes=int(stats["num_nodes"]))
    else:
        out.update(solved_by=str(sol.get_solved_by()), iterations=int(sol.get_lp_stats()["nb_iterations"]))
    if job["want_x"]:
        out["x"] = [float(v) for v in x]
    kept = []
    if job["keep_log"]:
        with open(log, encoding="utf-8", errors="replace") as handle:
            for line in handle:
                if any(p in line for p in job["keep_log"]) and not any(p in line for p in PRIVATE):
                    kept.append(line.rstrip())
    out["log"] = kept
    os.unlink(log)
    return out


def main(argv: list[str]) -> int:
    if not argv:
        print("cuopt_worker: solves a job file with cuOpt; lps.cuopt runs it under cuOpt's interpreter")
        return 0
    with open(argv[0], encoding="utf-8") as handle:
        job = json.load(handle)
    print(json.dumps(solve(job)))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
