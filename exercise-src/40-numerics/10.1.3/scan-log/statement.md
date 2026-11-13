A regional airline re-optimizes its maintenance schedule every night with HiGHS and keeps each
solve's log as a list of lines. Nobody reads the logs, so the operations team wants a scanner that
returns the lines worth reading, as short findings stored with each plan.

Write `scan(lines, max_span=1e6)`. It returns a list of findings, in the order their lines appear:

- a line that starts with `WARNING:` (after leading spaces) gives `"warning: <text>"`, where
  `<text>` is the rest of the line after `WARNING:`, with spaces trimmed at both ends;
- the range line that starts with `Matrix`, such as `  Matrix  [1e-01, 1e+09]`, gives
  `"matrix span <ratio>"` when the largest value divided by the smallest is above `max_span`, with
  the ratio written as `f"{ratio:.0e}"` (so `1e+10`);
- a report line such as `                    8.89e-07 (int. viol.)` gives
  `"<kind> violation <value>"` when its value is above 0, with `<kind>` `bound`, `integrality` or
  `row` for `(bound viol.)`, `(int. viol.)` and `(row viol.)`, and `<value>` the number exactly as
  the line writes it.

Every other line gives nothing. The tests use their own logs, in HiGHS's format. About fifteen
lines.
