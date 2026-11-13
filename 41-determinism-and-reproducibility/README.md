# 10.2. Determinism and Reproducibility

Why the same program on the same data can return a different plan, and how to make it stop: the
sources of a different answer (threads, clock limits, ties and Python's salted hashes), the seeds,
thread counts and work limits of HiGHS, CP-SAT, SCIP and Gurobi, tie-breaking among equally good
plans, snapshots, pinned versions and run manifests, and a harness that reruns a snapshot in fresh
processes and fails loudly when two manifests differ.

## Contents

1. [Where nondeterminism comes from: threads, time limits, ties](README_10.2.1.md)
2. [Seeds, threads and deterministic work limits, solver by solver](README_10.2.2.md)
3. [Alternative optima and deterministic tie-breaking](README_10.2.3.md)
4. [Versioned input snapshots, pinned solvers and run manifests](README_10.2.4.md)
5. [Building the deterministic run harness](README_10.2.5.md)
