The outage-week rules again. `clashing_rules(variables, rules)` is now given: it returns the names
CP-SAT reports as sufficient for infeasibility, which may include rules that are not to blame.
`feasible(variables, rules)` is also given: it says whether a list of rules can all hold at once.

The planners want the short list: a set of rules that clash, from which no rule can be dropped
without the rest becoming satisfiable. Write `minimal_clash(variables, rules)` that returns the
names of such a set, or `[]` if the rules can all hold.

Start from the names `clashing_rules` returns. Take them one at a time: if the set without that
rule is still infeasible, the rule is not needed, so leave it out for good; otherwise keep it. In
the notation of the previous practice, with $`S`$ the set kept so far and $`r \in S`$:

```math
S \leftarrow S \setminus \{r\} \quad \text{if the rules in } S \setminus \{r\} \text{ have no common solution}
```

CP-SAT may name every rule it was given, and a scenario may hold more than one clash. About
eight lines.
