A wind farm's maintenance model has thousands of rules in a few families: sensor checks per
turbine, an uptime target, quarterly budgets, staffing minimums. A deletion filter over every rule
would cost one solve per rule. The reliability engineer wants the cheaper two-pass version:

1. **Families.** Go through the families in the given order. Switch one family off (all its rules)
   while the families still kept stay on. If the rest is still infeasible, drop that family for
   good. If it becomes feasible, keep the family.
2. **Rules.** Go through the rules of the kept families, in the given order (family by family,
   rule by rule). Run the deletion filter on them, with every dropped family still switched off.

You get the families as a dict from family name to its list of rules, and an oracle,
`infeasible(rules) -> bool`, which says whether the model has no solution with exactly the rules
in the set switched on. Write `two_pass(families, infeasible)` returning `(kept, conflict)`: the
kept family names and the rules of the conflict, both in the given order. The model is known to be
infeasible with every rule on. No solver runs and no gap tolerance is involved: the oracle answers
each question exactly. About fifteen lines.
