A logistics team's nightly job tries a list of LP solvers in order: GPU solvers first, CPU solvers
after. The machine may have no GPU, a GPU solver may raise (out of memory, a driver fault), and a
solver may finish without an optimal answer. The job must never call a GPU solver on a machine
without a GPU, must not die because one solver failed, and must never hand on an answer its solver
did not call optimal.

Write `solve_with_fallback(model, solvers, gpu)` in `fallback.py`. Each solver is a dict with a
`name`, a `needs_gpu` flag and a `solve` function that takes the model and returns a dict with a
`"status"`. Go through the solvers in order:

- a solver that needs a GPU when `gpu` is False is not called, and logged as `"<name>: skipped (no GPU)"`;
- a solver that raises is logged as `"<name>: error"`, and the next one runs;
- any other solver is logged as `"<name>: <status>"`; the first whose status is `"Optimal"` is the answer.

Return `(result, log)`, with `result` None when no solver answered `"Optimal"`. The tests use fake
solvers, and one real LP solved with `highspy` on whatever the machine has:
`test_a_real_lp_is_solved_on_whatever_this_machine_has` tries HiGHS's GPU PDLP first on the GPU
image with a GPU. On a machine without a GPU it checks the CPU path only, and it says nothing about
the GPU part: no test is reported as skipped. About fifteen lines.
