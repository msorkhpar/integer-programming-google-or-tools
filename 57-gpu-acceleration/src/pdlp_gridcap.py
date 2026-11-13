"""OR-Tools' PDLP on the CPU, on the LP relaxation of GridCap small's start-year model.

Shows the iterations, how the tolerance sets where PDLP stops, that its answer is not a vertex, and what
restarts, rescaling (preconditioning) and adaptive steps each save. GridCap is fictional.
"""

from ortools.pdlp import solvers_pb2

from lps import gridcap_timing, highs, ortools_pdlp, relative_difference, violation

m, keys = gridcap_timing("small")
print(f"GridCap small, LP relaxation: {len(m['c'])} variables x[i,t] in [0, 1], {len(m['row_lb'])} rows, "
      f"{len(m['values'])} nonzeros")

exact = highs(m, "simplex")
at_bound = sum(v in (0.0, 1.0) for v in exact["x"])
print(f"HiGHS simplex (CPU): {exact['status']}, objective {exact['objective']:.6f}, "
      f"{exact['iterations']} iterations, {at_bound} of {len(keys)} values exactly 0 or 1")

print("\nPDLP (CPU, 1 thread): where it stops is set by the tolerance")
print("tolerance  iterations   objective      rel. error  max violation  values exactly 0 or 1")
for eps in (1e-2, 1e-4, 1e-6, 1e-8):
    r = ortools_pdlp(m, eps)
    print(f"{eps:9.0e}  {r['iterations']:10d}  {r['objective']:12.4f}  {relative_difference(r['objective'], exact['objective']):10.1e}"
          f"  {violation(m, r['x']):13.1e}  {sum(v in (0.0, 1.0) for v in r['x']):21d}")

traced = ortools_pdlp(m, 1e-8, record_every=64)
print("\nPDLP at 1e-8, every 64th iteration (its average iterate):")
print("iteration   primal obj.     dual obj.   primal res.  dual res.")
for k, primal, dual, pres, dres in traced["trace"][:8]:
    print(f"{k:9d}  {primal:12.3f}  {dual:12.3f}  {pres:11.1e}  {dres:9.1e}")

print("\nWhat PDLP adds to plain PDHG: iterations to 1e-6 with one feature switched off (limit 100,000)")
features = {
    "PDLP defaults": {},
    "no restarts": {"restart_strategy": solvers_pb2.PrimalDualHybridGradientParams.NO_RESTARTS},
    "no rescaling": {"l_inf_ruiz_iterations": 0, "l2_norm_rescaling": False},
    "constant step size": {"linesearch_rule": solvers_pb2.PrimalDualHybridGradientParams.CONSTANT_STEP_SIZE_RULE},
    "fixed primal weight": {"primal_weight_update_smoothing": 0.0},
}
for label, tweaks in features.items():
    r = ortools_pdlp(m, 1e-6, tweaks=tweaks, iteration_limit=100_000)
    print(f"{label:20s} {r['iterations']:7d} iterations  {r['status'].removeprefix('TERMINATION_REASON_')}")
