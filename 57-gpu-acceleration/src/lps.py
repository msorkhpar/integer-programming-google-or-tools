"""The module's models and solvers: one LP format, read by HiGHS, OR-Tools PDLP and cuOpt alike.

A model is a plain dict, so it can be written as JSON and read by cuOpt's interpreter in its own process
(cuOpt needs its own environment): the objective `c`, the constraint rows in compressed sparse row form (`offsets`, `indices`,
`values`), row bounds `row_lb <= A x <= row_ub`, variable bounds `lb <= x <= ub`, which variables are
`integer`, the sense `maximize`, and a `row_names` list that gives each row its label.
"""

from __future__ import annotations

import hashlib
import json
import math
import struct
import tempfile
import time
from pathlib import Path

from gpu import gpu_available, run_cuopt

INF = math.inf
SEED = 20261112                      # the toolchain's probes use the same seed, so their sizes compare
WORKER = Path(__file__).with_name("cuopt_worker.py")


def model(c, rows, lb, ub, integer, maximize):
    """rows: [(label, indices, values, row_lb, row_ub)] -> the module's model dict."""
    offsets, indices, values, rlb, rub, names = [0], [], [], [], [], []
    for label, idx, val, lo, hi in rows:
        indices += idx
        values += val
        offsets.append(len(indices))
        rlb.append(lo)
        rub.append(hi)
        names.append(label)
    return {"c": list(c), "offsets": offsets, "indices": indices, "values": values, "row_lb": rlb,
            "row_ub": rub, "lb": list(lb), "ub": list(ub), "integer": list(integer), "maximize": maximize,
            "row_names": names}


# ------------------------------------------------------------------ the models
def transport(n: int):
    """A balanced transportation LP: n sources, n sinks, integer costs 1..99 from a fixed-seed generator."""
    state, costs = SEED, []
    for _ in range(n * n):
        state = (6364136223846793005 * state + 1442695040888963407) % 2**64
        costs.append(float(1 + (state >> 33) % 99))
    supply = [n * 10 + (i % 7) for i in range(n)]
    total = sum(supply)
    demand = [total // n + (1 if j < total % n else 0) for j in range(n)]
    rows = [(f"supply_{i}", [i * n + j for j in range(n)], [1.0] * n, -INF, float(supply[i])) for i in range(n)]
    rows += [(f"demand_{j}", [i * n + j for i in range(n)], [1.0] * n, float(demand[j]), INF) for j in range(n)]
    return model(costs, rows, [0.0] * (n * n), [INF] * (n * n), [False] * (n * n), False)


def gridcap_timing(size: str = "small", integer: bool = False, seed: int = 2027):
    """GridCap's start-year model: x[i,t] for each project i and start year t, budgets per year.

    Returns the model and the (project, year) key of each variable. With integer=False it is the LP
    relaxation, 0 <= x <= 1.
    """
    from gridcap import generate

    pf = generate(size, seed)
    keys = [(p.project_id, t) for p in pf.projects for t in p.starts()]
    col = {k: n for n, k in enumerate(keys)}
    c = [float(pf.project(i).npv[t]) for i, t in keys]
    rows = []
    for p in pf.projects:
        idx = [col[(p.project_id, t)] for t in p.starts()]
        lo = 1.0 if p.must_do else -INF
        rows.append(((f"must_{p.project_id}" if p.must_do else f"once_{p.project_id}"), idx, [1.0] * len(idx), lo, 1.0))
    for g in sorted({p.alt_group for p in pf.projects if p.alt_group}):
        idx = [col[(p.project_id, t)] for p in pf.projects if p.alt_group == g for t in p.starts()]
        rows.append((f"alt_{g}", idx, [1.0] * len(idx), -INF, 1.0))
    for y in pf.years:
        idx, val = [], []
        for (i, t), n in col.items():
            amount = pf.project(i).spend(t).get(y, 0)
            if amount:
                idx.append(n)
                val.append(float(amount))
        rows.append((f"budget_{y}", idx, val, -INF, float(pf.budget[y])))
    m = model(c, rows, [0.0] * len(keys), [1.0] * len(keys), [integer] * len(keys), True)
    return m, keys


# ------------------------------------------------------------------ checks shared by every solver
def violation(m: dict, x) -> float:
    """The largest amount by which x breaks a row or a bound (0.0 when it breaks none)."""
    worst = 0.0
    for r in range(len(m["row_lb"])):
        a, b = m["offsets"][r], m["offsets"][r + 1]
        activity = sum(m["values"][k] * x[m["indices"][k]] for k in range(a, b))
        worst = max(worst, m["row_lb"][r] - activity, activity - m["row_ub"][r])
    for j, v in enumerate(x):
        worst = max(worst, m["lb"][j] - v, v - m["ub"][j])
    return max(worst, 0.0)


def relative_difference(a: float, b: float) -> float:
    """|a - b| / max(1, |b|): how far a is from the reference b."""
    return abs(a - b) / max(1.0, abs(b))


def digest(values) -> str:
    """The first 16 hex digits of the SHA-256 of the IEEE-754 bytes: equal digests mean equal bits."""
    return hashlib.sha256(struct.pack(f"<{len(values)}d", *values)).hexdigest()[:16]


# ------------------------------------------------------------------ HiGHS (highspy)
def highs(m: dict, solver: str = "simplex", threads: int = 1, time_limit: float | None = None,
          gap: float | None = None, tolerance: float | None = None) -> dict:
    """Solve with highspy: "simplex" or "ipm" on the CPU, "pdlp" on the GPU only.

    `gap` is a MILP's relative gap; `tolerance` sets the LP method's own optimality tolerance.
    """
    if solver == "pdlp" and not gpu_available():
        # The CUDA build's PDLP has no CPU path: without a GPU it kills the process.
        raise RuntimeError("highspy's PDLP runs here only on a GPU; check gpu_available() first")
    import highspy

    h = highspy.Highs()
    h.setOptionValue("output_flag", False)          # else cuPDLP-C prints its log on stdout
    h.setOptionValue("threads", threads)
    h.setOptionValue("random_seed", 0)
    h.setOptionValue("solver", solver if not any(m["integer"]) else "choose")
    if time_limit is not None:
        h.setOptionValue("time_limit", float(time_limit))
    if gap is not None:
        h.setOptionValue("mip_rel_gap", float(gap))
    if tolerance is not None:
        names = {"pdlp": ["pdlp_optimality_tolerance"], "ipm": ["ipm_optimality_tolerance"],
                 "simplex": ["primal_feasibility_tolerance", "dual_feasibility_tolerance"]}[solver]
        for name in names:
            h.setOptionValue(name, float(tolerance))
    inf = highspy.kHighsInf
    lp = highspy.HighsLp()
    lp.num_col_, lp.num_row_ = len(m["c"]), len(m["row_lb"])
    lp.col_cost_ = m["c"]
    lp.col_lower_ = [max(v, -inf) for v in m["lb"]]
    lp.col_upper_ = [min(v, inf) for v in m["ub"]]
    lp.row_lower_ = [max(v, -inf) for v in m["row_lb"]]
    lp.row_upper_ = [min(v, inf) for v in m["row_ub"]]
    lp.a_matrix_.format_ = highspy.MatrixFormat.kRowwise
    lp.a_matrix_.start_, lp.a_matrix_.index_, lp.a_matrix_.value_ = m["offsets"], m["indices"], m["values"]
    if any(m["integer"]):
        lp.integrality_ = [highspy.HighsVarType.kInteger if i else highspy.HighsVarType.kContinuous
                           for i in m["integer"]]
    lp.sense_ = highspy.ObjSense.kMaximize if m["maximize"] else highspy.ObjSense.kMinimize
    h.passModel(lp)
    start = time.perf_counter()
    h.run()
    seconds = time.perf_counter() - start
    info = h.getInfo()
    x = list(h.getSolution().col_value)
    out = {"solver": "highs-mip" if any(m["integer"]) else f"highs-{solver}", "status": h.modelStatusToString(h.getModelStatus()),
           "objective": info.objective_function_value, "x": x, "seconds": seconds,
           "iterations": {"simplex": info.simplex_iteration_count, "ipm": info.ipm_iteration_count,
                          "pdlp": info.pdlp_iteration_count}[solver] if not any(m["integer"]) else None,
           "max_primal_infeasibility": info.max_primal_infeasibility,
           "max_dual_infeasibility": info.max_dual_infeasibility}
    if any(m["integer"]):
        out.update(bound=info.mip_dual_bound, gap=info.mip_gap, nodes=info.mip_node_count)
    return out


# ------------------------------------------------------------------ OR-Tools PDLP (CPU), its direct API
def ortools_pdlp(m: dict, eps: float = 1e-6, record_every: int = 0, threads: int = 1,
                 tweaks: dict | None = None, iteration_limit: int | None = None) -> dict:
    """Solve the LP with OR-Tools' PDLP on the CPU, stopping at relative and absolute tolerance eps.

    `tweaks` sets fields of PrimalDualHybridGradientParams by name, e.g. {"l2_norm_rescaling": False}.
    """
    import numpy as np
    import scipy.sparse
    from ortools.pdlp import solve_log_pb2, solvers_pb2
    from ortools.pdlp.python import pdlp

    sign = -1.0 if m["maximize"] else 1.0             # PDLP minimises: max c'x is min -c'x
    qp = pdlp.QuadraticProgram()
    qp.objective_vector = np.array(m["c"]) * sign
    qp.constraint_lower_bounds = np.array(m["row_lb"])
    qp.constraint_upper_bounds = np.array(m["row_ub"])
    qp.variable_lower_bounds = np.array(m["lb"])
    qp.variable_upper_bounds = np.array(m["ub"])
    qp.constraint_matrix = scipy.sparse.csr_matrix(
        (m["values"], m["indices"], m["offsets"]), shape=(len(m["row_lb"]), len(m["c"]))).tocsc()
    params = solvers_pb2.PrimalDualHybridGradientParams()
    criteria = params.termination_criteria.simple_optimality_criteria
    criteria.eps_optimal_relative = eps
    criteria.eps_optimal_absolute = eps
    params.num_threads = threads
    params.verbosity_level = 0
    params.record_iteration_stats = record_every > 0
    for name, value in (tweaks or {}).items():
        setattr(params, name, value)
    if iteration_limit is not None:
        params.termination_criteria.iteration_limit = iteration_limit
    start = time.perf_counter()
    result = pdlp.primal_dual_hybrid_gradient(qp, params)
    seconds = time.perf_counter() - start
    log = result.solve_log
    x = [float(v) for v in result.primal_solution]
    out = {"solver": "ortools-pdlp", "status": solve_log_pb2.TerminationReason.Name(log.termination_reason),
           "objective": float(sign * sum(ci * xi for ci, xi in zip(qp.objective_vector, x))), "x": x,
           "seconds": seconds, "iterations": log.iteration_count}
    if record_every:
        trace = []
        for stats in log.iteration_stats:
            if stats.iteration_number % record_every == 0:
                for ci in stats.convergence_information:
                    if ci.candidate_type == solve_log_pb2.POINT_TYPE_AVERAGE_ITERATE or len(
                            stats.convergence_information) == 1:
                        trace.append((stats.iteration_number, sign * ci.primal_objective, sign * ci.dual_objective,
                                      ci.l2_primal_residual, ci.l2_dual_residual))
                        break
        out["trace"] = trace
    return out


# ------------------------------------------------------------------ cuOpt (its own venv and process)
def cuopt(m: dict, method: str = "pdlp", settings: dict | None = None, want_x: bool = False,
          keep_log: tuple[str, ...] = ()) -> dict:
    """Solve with NVIDIA cuOpt in a process of its own; needs gpu_available()."""
    with tempfile.TemporaryDirectory() as folder:
        job = Path(folder) / "job.json"
        job.write_text(json.dumps({"model": m, "method": method, "settings": settings or {}, "want_x": want_x,
                                   "keep_log": list(keep_log)}), encoding="utf-8")
        done = run_cuopt(WORKER, job)
    if done.returncode != 0:
        raise RuntimeError(f"cuOpt worker failed: {done.stderr[-500:]}")
    return json.loads(done.stdout.strip().splitlines()[-1])
