A port authority plans its capital works with a MILP that **maximises** value, and its nightly
service now has GPU answers on hand. Its rule: a GPU answer may serve as an **LP bound** or as a
**start** for the CPU solver, each verified on the CPU, and never as the **plan of record**.

Write `usable(use, gpu, cpu)` in `answers.py`, returning `(accepted, value)` where `value` is the
thing to use when accepted and a reason when not:

- `use == "plan"`: never; the reason is `"the plan of record runs on the CPU"`.
- `use == "bound"`: `gpu` is `{"status", "objective"}` from an LP relaxation and `cpu` is
  `{"objective"}` from a CPU solve of the same LP. Refuse with `"not optimal"` unless the GPU status
  is `"Optimal"`; refuse with `"not confirmed"` unless the two objectives differ by at most
  $`10^{-6}`$ relatively (divided by $`\max(1, \lvert\text{CPU objective}\rvert)`$). Otherwise use the
  **larger** of the two values: a bound on a maximisation must not understate the cap.
- `use == "start"`: `gpu` is `{"status", "x"}` from a MILP solver and `cpu` is `{"feasible",
  "integral"}`, the CPU check of `x`. Use `x` when both checks passed, whatever the status label
  says; otherwise refuse with `"fails the check"`.

About fifteen lines.
