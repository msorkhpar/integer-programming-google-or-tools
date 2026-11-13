A delivery company tunes its routing solver on last year's models, one per depot per month. Months of
one depot share roads and customers, so if January's model of a depot is in the training set and
February's in the test set, the test is not a test: the tuner has, in effect, seen it. The team
uses $`k`$-fold cross-validation (tune on all folds but one, test on the one left out, and repeat
for each fold), and every depot must sit wholly inside one fold.

With $`N`$ the instance names, $`g(n)`$ the group (depot) of instance $`n`$, and $`G`$ the groups in
sorted order $`g_0, g_1, \dots`$, write before you code: which fold group $`g_j`$ goes to, which
instances fold $`f`$ holds, and, for a split into a training set $`A`$ and a test set $`B`$, the set
of groups that leak.

Write `folds(names, group_of, k)` and `leaks(train, test, group_of)` in `validation.py`. `folds`
returns `k` lists, the names in each sorted; `leaks` returns a set of groups. The tests pass small
lists; no solver runs. About six lines.
