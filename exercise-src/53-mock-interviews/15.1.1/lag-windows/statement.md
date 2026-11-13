A water utility's planners write their dependency rules in whatever words come to hand: "R7 starts
two years after R3 starts", "R9 starts a year after R4 is finished", "R5 must be finished no earlier
than R2 is finished". Before any row is written, every rule is turned into one start-to-start lag
$`L`$, meaning the child may start in year $`t`$ only if the parent started in some year
$`s \le t - L`$. A renewal of duration $`d`$ started in year $`s`$ finishes at $`s + d`$.

Write two functions in `lags.py`:

- `start_to_start(kind, lag, parent_duration, child_duration)` returns $`L`$ for a lag measured
  between the two events `kind` names: `"SS"` (parent's start to child's start), `"FS"` (parent's
  finish to child's start), `"FF"` (parent's finish to child's finish) or `"SF"` (parent's start to
  child's finish). The child's event must come at least `lag` years after the parent's. $`L`$ may be
  negative.
- `usable_child_years(parent_starts, child_starts, lag)` returns, in increasing order, the child's
  start years that at least one of the parent's start years serves, for a start-to-start `lag`. The
  others can be deleted from the model before it is built.

Write each conversion as an inequality between the two events first, then solve it for the child's
start. The tests use their own numbers. About ten lines in total.
