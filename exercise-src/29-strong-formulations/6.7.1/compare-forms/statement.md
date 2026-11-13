A modeling team keeps several formulations of the same rules and wants a quick, honest report of
which is stronger before anyone writes the row-by-row proof. You have, for each formulation, a
function that builds its LP relaxation with a given objective, and a list of objectives to try.

Write `compare(build_a, build_b, objectives, sense="max")` in `compare.py`. It solves both
relaxations for every objective (GLOP is fine; `lp_value` is given) and returns:

- `"a"` if $`A`$'s bound is at least as tight as $`B`$'s on every objective and strictly tighter on
  at least one, and `"b"` the other way round;
- `"neither"` if each is strictly tighter on some objective, which shows that neither region
  contains the other;
- `"same"` if the bounds agree on every objective.

Decide first what "tighter" means for a maximization and for a minimization, using the rule
$`z_{IP} \le z_{LP}`$ (maximizing) and its mirror. Compare with the tolerance `TOLERANCE`, since a
solver's values carry rounding noise.

The tests use small formulations of "at most one" and "at least one" of two decisions, so you can
check each answer by hand. About fifteen lines.
