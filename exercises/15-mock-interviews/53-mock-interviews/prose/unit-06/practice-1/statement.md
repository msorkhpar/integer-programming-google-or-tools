A telecom operator wants every plan its optimizer returns checked by code that shares nothing with
the model: it reads only the data and the plan. Write `broken_rules(plan, projects, limits)` in
`checker.py`. `plan` is the set of funded project ids. It returns the sorted list of labels of every
rule the plan breaks, and an empty list when it breaks none:

- `"budget"`: the plan's total cost is above `limits.budget`;
- `"crews"`: its total crew-weeks are above `limits.crew`;
- `"region_<r>"`: more projects in region `r` than `limits.region_cap[r]`; a region with no entry
  in `limits.region_cap` has no cap, however many of its projects are funded;
- `"conflict_<a>_<b>"`: both projects of a pair in `limits.conflicts` are funded;
- `"needs_<a>_<b>"`: for a pair `(a, b)` in `limits.needs`, `a` is funded without `b`.

Report every broken rule, not only the first. About fifteen lines.
