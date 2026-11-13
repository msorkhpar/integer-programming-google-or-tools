This is the screen's whiteboard, coded. A telecom operator chooses tower upgrades: each has a `cost`
($k), `crew` weeks, a `region` and a `value`. `upgrades.py` already has one binary per project and
the objective, the most value. Write `add_rules(model, x, projects, limits)` with every rule:

- the total cost is at most `limits.budget`, and the total crew-weeks at most `limits.crew`;
- at most `limits.region_cap[r]` projects in each region `r`; a region with no entry in
  `limits.region_cap` has no cap;
- for each pair in `limits.conflicts`, not both;
- for each pair `(a, b)` in `limits.needs`, `a` only if `b`.

Write the formulation first (sets, parameters, variables with domains, labelled rows with
quantifiers). The tests fix plans and ask HiGHS whether the model accepts them, so any correct
formulation passes. About ten lines.
