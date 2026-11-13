"""One LP, solved on the GPU when one is there and answers, on the CPU otherwise, and checked against a
CPU reference within a stated tolerance. GridCap is fictional.

The CPU path runs everywhere and prints first; the GPU path runs and prints only where gpu_available().
"""

from gpu import describe, gpu_available

from lps import gridcap_timing, highs, relative_difference, transport, violation

TOLERANCE = 1e-6          # relative, on the objective and on the rows (scaled by the largest bound)


def solve_lp(m: dict, use_gpu: bool | None = None) -> tuple[dict, list[str]]:
    """GPU PDLP when there is a GPU and it reports Optimal; HiGHS interior point on the CPU otherwise."""
    if use_gpu is None:
        use_gpu = gpu_available()
    tried = []
    if use_gpu:                                    # never solver="pdlp" without a GPU: it kills the process
        result = highs(m, "pdlp")
        tried.append(f"{result['solver']} {result['status']}")
        if result["status"] == "Optimal":
            return result, tried
    result = highs(m, "ipm")
    tried.append(f"{result['solver']} {result['status']}")
    return result, tried


def agrees(result: dict, reference: dict, m: dict, tol: float = TOLERANCE) -> bool:
    """Same answer within tol: the objective, relatively, and every row and bound, scaled by the largest one."""
    scale = max([1.0] + [abs(v) for v in m["row_lb"] + m["row_ub"] if abs(v) != float("inf")])
    return (relative_difference(result["objective"], reference["objective"]) <= tol
            and violation(m, result["x"]) <= tol * scale)


def main() -> None:
    models = {"GridCap small LP": gridcap_timing("small")[0], "transport 100x100": transport(100)}
    references = {name: highs(m, "simplex") for name, m in models.items()}

    print(f"reference: HiGHS simplex on the CPU; tolerance {TOLERANCE:.0e}")
    print("CPU path (runs on every machine):")
    for name, m in models.items():
        result, tried = solve_lp(m, use_gpu=False)
        print(f"  {name:18s} tried {', '.join(tried):22s} objective {result['objective']:14.3f}"
              f"  agrees: {agrees(result, references[name], m)}")

    if gpu_available():
        print(describe())
        print("GPU path:")
        for name, m in models.items():
            result, tried = solve_lp(m)
            print(f"  {name:18s} tried {', '.join(tried):38s} objective {result['objective']:14.3f}"
                  f"  rel. diff {relative_difference(result['objective'], references[name]['objective']):.1e}"
                  f"  agrees: {agrees(result, references[name], m)}")
        refused = highs(models["GridCap small LP"], "pdlp")
        print(f"  the refused GPU answer: status {refused['status']}, objective rel. diff "
              f"{relative_difference(refused['objective'], references['GridCap small LP']['objective']):.1e}, "
              f"max primal infeasibility {refused['max_primal_infeasibility']:.1e}, "
              f"max dual infeasibility {refused['max_dual_infeasibility']:.1e}")


if __name__ == "__main__":
    main()
