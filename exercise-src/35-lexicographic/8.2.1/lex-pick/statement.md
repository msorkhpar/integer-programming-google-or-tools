A city scores a handful of road-resurfacing packages by hand before it commits to a model. Each
package has a value for every objective, for example
`{"safety": 42.0, "cost": 3.1, "noise": -6.0}`. The council ranks the objectives and gives each one a
sense and tolerances, as a list of levels in priority order:

```python
(name, maximize, abs_tol, rel_tol)     # e.g. ("safety", True, 0.0, 0.05)
```

The packages the council accepts are found level by level. At each level, take the best value
$`\Gamma`$ of that objective **among the packages still accepted**, and keep only the packages within
the allowed loss $`\delta = \max(\text{abs\_tol},\ \text{rel\_tol} \cdot |\Gamma|)`$ of it: at least
$`\Gamma - \delta`$ for a maximized objective, at most $`\Gamma + \delta`$ for a minimized one.

Write `accepted(packages, levels)`. `packages` maps a package name to its values; return the sorted
list of the names that survive every level. About ten lines; no solver is needed for a handful of
packages.
