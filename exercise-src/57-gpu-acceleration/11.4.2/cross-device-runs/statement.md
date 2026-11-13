A routing team solves the same LP on laptops (CPU only), on a build server, and on a GPU
workstation, and keeps a record of each run: the `device` (`"cpu"` or `"gpu"`), the `solver`, the
`objective`, and a `digest` of the solution's bits. Before a release they want one function that
says whether a set of runs agrees, by a rule written down once:

- one CPU run is the reference: the first CPU run in the list. With no CPU run there is no
  reference, and the result is exactly `["no CPU reference"]`: no other check runs, so not even a
  repeat that differs is reported until a CPU run is added;
- runs of the same solver on the same device are repeats, and a repeat must give the same digest
  and objective as that pair's first run, else `"<device>/<solver>: repeat differs"`;
- every run's objective must be within `tol` of the reference's, relatively (divided by
  $`\max(1, \lvert\text{reference}\rvert)`$), else `"<device>/<solver>: off the reference"`.

Write `check_runs(runs, tol)` in `runs.py`, returning the problems sorted, each once; an empty list
means the runs agree. One test,
`test_real_runs_on_this_machine_agree_and_a_run_off_by_a_thousandth_is_caught`, solves a small LP
with `highspy` on this machine; on the GPU image with a GPU it adds two GPU PDLP runs. On a machine
without a GPU that test runs its CPU part only, and it says nothing about the GPU part: no test is
reported as skipped. About fifteen lines.
