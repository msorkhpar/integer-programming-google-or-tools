A retailer solves a picking-route MIP for each of its warehouses every night and wants to tune the
solver once for all of them. The team has already run every configuration on every warehouse model
and stored the deterministic work in `work[(instance, config)]`. The first configuration in
`configs` is the solver's default. The warehouses are split, before anyone looks at the numbers,
into training instances, on which the configuration is chosen, and held-out test instances, on
which it is reported.

With $`w_{i,c}`$ the work of configuration $`c`$ on instance $`i`$ and $`s`$ the shift, write down
before you code: the score $`S_c(I)`$ of a configuration on a set of instances $`I`$ (the shifted
geometric mean of lesson 5.4.2, given as `sgm`), the chosen configuration $`c^*`$ in terms of the
training set, and the two numbers to report, each a ratio to the default $`c_0`$.

Write `score(work, config, instances, shift)` and `tune(work, configs, train, test, shift)` in
`tuning.py`; `tune` returns `(chosen, train ratio, test ratio)`. When two configurations score the
same on the training set, the earlier one in `configs` wins. The tests pass small tables; no solver
runs. About eight lines.
