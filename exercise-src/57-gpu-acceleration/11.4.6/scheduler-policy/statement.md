A rail operator's planning service runs three kinds of job: answers it **publishes** (timetables
the public sees), **exploratory** runs for analysts, and LP **bounds**. It runs on laptops, on
servers and on one GPU machine, and the team wants every decision about how a job runs in one
frozen object, `Policy(device, solver, method, threads, tolerance, verify)` (given in `policy.py`).
A job is `{"kind": "lp" | "milp", "nonzeros": int, "use": "publish" | "explore" | "bound"}`; a
machine is `{"gpu": bool, "cuopt": bool, "cores": int}`.

The rules, in order:

1. A published answer must repeat: CPU, HiGHS, one thread, never verified elsewhere. A MILP uses
   `"branch-and-bound"` at gap `1e-4`; an LP uses `"simplex"` at `1e-7`.
2. Any other MILP goes to cuOpt (`"gpu"`, `"cuopt"`, `"milp"`, all the machine's cores, gap `1e-2`)
   when the machine has a GPU **and** cuOpt; otherwise to HiGHS's `"branch-and-bound"` on the CPU,
   with 4 threads or the machine's cores if fewer, gap `1e-2`.
3. Any other LP with at least 500,000 nonzeros goes to HiGHS's `"pdlp"` on the GPU (one thread,
   `1e-6`) when there is a GPU; otherwise to HiGHS's `"ipm"` on the CPU, with 4 threads or fewer as
   above, at `1e-8`.
4. Every other LP: CPU, HiGHS `"simplex"`, one thread, `1e-7`.

Every answer from a GPU is verified on the CPU (`verify=True`); no CPU answer is. Write
`decide(job, machine)` in `policy.py`. About fifteen lines.
