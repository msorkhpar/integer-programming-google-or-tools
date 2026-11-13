A school district (an invented one, like its data) has replaced its roof-planning model and wants a
back-test: today's model was rerun on the input snapshot of each past planning cycle, and its plans
must be set beside the plans those cycles approved. The district's reviewers read one summary line
per cycle.

The docstring of `roof_backtest.py` gives the two inputs' shapes; a plan maps each funded roof to
its start year. Write `summarize(archive, rerun)`, returning one dict per archived cycle, in archive
order:

- for a cycle with no entry in `rerun`: `{"cycle": year, "missing": True}`, since a cycle that was
  not rerun has no comparison to make;
- otherwise `{"cycle", "missing": False, "kept", "moved", "added", "dropped", "agreement"}`, where
  `kept` counts approved roofs today's plan funds in the same year, `moved` those it funds in
  another year, `added` roofs only today's plan funds, `dropped` approved roofs it does not fund,
  and `agreement` is kept divided by the number of approved roofs, rounded to 3 decimals. When the
  cycle approved nothing, agreement is `1.0` if today's plan funds nothing too, and `0.0` if it
  funds anything.

About fifteen lines.
