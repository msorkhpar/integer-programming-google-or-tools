"""Run each solver twice on the same LP and compare the answers bit for bit.

CPU solvers run everywhere; the GPU solvers (HiGHS PDLP, cuOpt PDLP, cuOpt's concurrent default) only where
gpu_available(). "same bits" compares the objective and every value of the solution as IEEE-754 bytes.
"""

from gpu import describe, gpu_available

from lps import cuopt, digest, gridcap_timing, highs, ortools_pdlp, transport


def same_bits(a: dict, b: dict) -> bool:
    return digest([a["objective"]]) == digest([b["objective"]]) and a.get("digest", digest(a.get("x", []))) == b.get(
        "digest", digest(b.get("x", [])))


METHODS = {"1": "PDLP", "2": "dual simplex", "3": "barrier"}       # cuOpt's get_solved_by(), as SolverMethod numbers

models = {"GridCap small LP": gridcap_timing("small")[0], "transport 100x100": transport(100)}
cpu_runs = {
    "HiGHS simplex, 1 thread": lambda m: highs(m, "simplex"),
    "HiGHS interior point, 1 thread": lambda m: highs(m, "ipm"),
    "OR-Tools PDLP, 1 thread": lambda m: ortools_pdlp(m, 1e-6),
    "OR-Tools PDLP, 4 threads": lambda m: ortools_pdlp(m, 1e-6, threads=4),
}
print("CPU, two runs in one process:")
for name, m in models.items():
    for label, run in cpu_runs.items():
        print(f"  {name:18s} {label:31s} same bits: {same_bits(run(m), run(m))}")
one, four = ortools_pdlp(models["transport 100x100"], 1e-6), ortools_pdlp(models["transport 100x100"], 1e-6, threads=4)
print(f"OR-Tools PDLP, 1 thread against 4 threads on transport 100x100: same bits {same_bits(one, four)}, "
      f"iterations {one['iterations']} and {four['iterations']}")

print("the answers' digests (equal digests mean equal bits; compare them across machines and images):")
for label, run in list(cpu_runs.items())[:3]:
    r = run(models["transport 100x100"])
    print(f"  transport 100x100  {label:31s} objective {r['objective']!r:20s} x {digest(r['x'])}")

if gpu_available():
    print(describe())
    print("GPU, two runs (cuOpt: each in a process of its own):")
    for name, m in models.items():
        print(f"  {name:18s} {'HiGHS PDLP':31s} same bits: {same_bits(highs(m, 'pdlp'), highs(m, 'pdlp'))}")
        print(f"  {name:18s} {'cuOpt PDLP':31s} same bits: {same_bits(cuopt(m, 'pdlp'), cuopt(m, 'pdlp'))}")
    big = transport(300)
    print("cuOpt's default method (concurrent) on transport 300x300, three runs:")
    for k in range(3):
        r = cuopt(big, "concurrent")
        print(f"  run {k + 1}: solved by {METHODS[r['solved_by']]}, objective {r['objective']:,.4f}, digest {r['digest']}")
