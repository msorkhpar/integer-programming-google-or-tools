"""A GridCap capital-planning MILP solved by HiGHS on one CPU thread (twice) and, where there is a GPU, by
cuOpt (twice, and twice more in its determinism mode). Every plan is checked before it is believed: rows,
integrality, and its objective against the best bound any solver proved. GridCap is fictional.
"""

from gpu import describe, gpu_available

from lps import cuopt, digest, gridcap_timing, highs, violation

GAP = 1e-3                     # stop at a relative gap of 0.1%, the same target for both solvers



def check(m: dict, run: dict, best_bound: float, gap: float = GAP) -> tuple[bool, str]:
    """Rows and bounds kept, every value integral, and the objective within `gap` of the best proven bound
    (a maximization: no plan is worth more than any solver's bound)."""
    x = run["x"]
    broken = violation(m, x)
    integral = max(abs(v - round(v)) for v in x)
    shortfall = (best_bound - run["objective"]) / abs(best_bound)
    ok = broken <= 1e-6 and integral <= 1e-5 and shortfall <= gap
    return ok, (f"violation {broken:.0e}, integrality {integral:.0e}, "
                f"{shortfall:.2e} below the best bound: {'accepted' if ok else 'refused'}")


def main() -> None:
    m, keys = gridcap_timing("medium", integer=True)
    print(f"GridCap medium, start-year model: {len(keys)} binaries x[i,t], {len(m['row_lb'])} rows; "
          f"relative gap target {GAP:.0e}")

    def plan(run: dict) -> set:
        return {keys[j] for j, v in enumerate(run["x"]) if v > 0.5}

    first, second = (highs(m, threads=1, gap=GAP) for _ in range(2))
    print(f"HiGHS, 1 thread: {first['status']}, objective {first['objective']:,.0f}, bound {first['bound']:,.0f}, "
          f"{first['nodes']} nodes; second run same bits: {digest(first['x']) == digest(second['x'])}")
    print(f"  check: {check(m, first, first['bound'])[1]}")

    if gpu_available():
        print(describe())
        keep = ("GPUFJ", "concurrent mode", "Root relaxation solution found", "Solving a problem with")
        runs = [cuopt(m, settings={"mip_relative_gap": GAP, "time_limit": 60}, want_x=True, keep_log=keep)
                for _ in range(2)]
        best = min(first["bound"], *(r["bound"] for r in runs))
        print(f"HiGHS's two runs took {first['seconds']:.1f} s and {second['seconds']:.1f} s on one thread")
        print(f"best bound proved by any solver: {best:,.0f}")
        for k, r in enumerate(runs, 1):
            print(f"cuOpt run {k}: {r['status']}, objective {r['objective']:,.0f}, its bound {r['bound']:,.0f}, "
                  f"gap {r['gap']:.1e}, {r['nodes']:,} nodes, {r['solver_seconds']:.1f} s")
            print(f"  check: {check(m, r, best)[1]}")
            print(f"  starts that differ from HiGHS's plan: {len(plan(r) ^ plan(first))}")
        print(f"cuOpt's two plans the same: {plan(runs[0]) == plan(runs[1])}, same bits: {runs[0]['digest'] == runs[1]['digest']}")
        print("cuOpt's log, the lines that say where the work runs:")
        for line in runs[0]["log"]:
            print(f"  {line}")
        det = [cuopt(m, settings={"mip_relative_gap": GAP, "time_limit": 20, "mip_determinism_mode": 1}, want_x=True)
               for _ in range(2)]
        for k, r in enumerate(det, 1):
            print(f"cuOpt determinism mode, run {k}: {r['status']}, objective {r['objective']:,.0f}, gap {r['gap']:.1e}, "
                  f"{r['nodes']:,} nodes, {r['solver_seconds']:.1f} s")
        print(f"  the two runs same bits: {det[0]['digest'] == det[1]['digest']}")


if __name__ == "__main__":
    main()
