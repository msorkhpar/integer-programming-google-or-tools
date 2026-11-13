"""PDLP on the CPU and the GPU, against HiGHS's interior point method, on transportation LPs of growing size.

    python3 compare.py [n ...]          # n x n transportation LPs; default 30 100 300

Runs what the machine has: HiGHS interior point and OR-Tools PDLP on the CPU everywhere; HiGHS's GPU PDLP
(cuPDLP-C) and cuOpt's PDLP where gpu_available(). Each solver stops at its own default tolerance. Times are
wall seconds of the solve alone (cuOpt: its own solve time), and change from machine to machine and run to run.
"""

import sys

from gpu import describe, gpu_available

from lps import cuopt, highs, ortools_pdlp, relative_difference, transport

sizes = [int(a) for a in sys.argv[1:]] or [30, 100, 300]
gpu = gpu_available()
times, gpu_rows = [], []
if gpu:                       # the first GPU solve in a process also starts CUDA: measure it apart
    tiny = transport(10)
    first, second = highs(tiny, "pdlp"), highs(tiny, "pdlp")

print("Every answer against HiGHS interior point (CPU), relative difference of the objective")
print("    n   variables      IPM objective   OR-Tools PDLP (CPU)  iterations")
for n in sizes:
    m = transport(n)
    ipm = highs(m, "ipm")
    pdlp = ortools_pdlp(m, 1e-6)
    print(f"{n:5d}  {n * n:10,d}  {ipm['objective']:17,.2f}  {relative_difference(pdlp['objective'], ipm['objective']):19.0e}"
          f"  {pdlp['iterations']:10,d}")
    row = {"n": n, "highs-ipm (CPU)": ipm["seconds"], "ortools-pdlp (CPU)": pdlp["seconds"]}
    if gpu:
        hg = highs(m, "pdlp")
        co = cuopt(m, "pdlp")
        row.update({"highs-pdlp (GPU)": hg["seconds"], "cuopt-pdlp (GPU)": co["solver_seconds"]})
        gpu_rows.append((n, hg, co, ipm))
    times.append(row)

if gpu:
    print(describe())
    print("the GPU answers against HiGHS interior point (CPU), relative difference of the objective")
    print("    n   HiGHS PDLP (GPU)  iterations   cuOpt PDLP (GPU)  iterations  cuOpt max violation")
    for n, hg, co, ipm in gpu_rows:
        print(f"{n:5d}  {relative_difference(hg['objective'], ipm['objective']):16.0e}  {hg['iterations']:10,d}"
              f"  {relative_difference(co['objective'], ipm['objective']):17.0e}  {co['iterations']:10,d}"
              f"  {co['violation']:19.0e}")

print("seconds (this machine, this run):")
columns = [c for c in times[0] if c != "n"]
print("    n  " + "  ".join(f"{c:>18s}" for c in columns))
for row in times:
    print(f"{row['n']:5d}  " + "  ".join(f"{row[c]:18.3f}" for c in columns))

if gpu:
    print(f"start-up: a 100-variable LP by HiGHS PDLP on the GPU, the process's first GPU solve "
          f"{first['seconds']:.3f} s, the same LP again {second['seconds']:.3f} s")
