A transit agency reviews its bus fleet once a year. For each bus the plan picks one of four
options: `"keep"` it as it is, `"refurbish"` it, replace it with a `"diesel"` bus, or replace it
with an `"electric"` one. The model in `fleet.py` has a binary `y[bid, option]` for every bus and
every option. The rules:

- **One option per bus.** Every bus gets exactly one of the four options; "keep" is a decision like
  the others.
- **Chargers.** The depot has `chargers` charging bays, so at most that many buses can be replaced
  with electric ones.
- **Age.** A bus older than `max_age` years may not be kept: it must be refurbished or replaced. A
  bus exactly `max_age` years old may still be kept.

Write `add_fleet_rules(model, y, buses, chargers, max_age)` so that the model allows exactly the
plans that keep the three rules.

The model so far, with $`B`$ the buses and $`O`$ the four options:

```math
\begin{aligned}
& y_{b,o} \in \{0, 1\} && \forall b \in B,\ o \in O && \text{(bus } b \text{ gets option } o\text{)} \\
& \text{?} && && \text{(your rows)}
\end{aligned}
```

Name the remaining parameters (each bus's age, the chargers, the age limit) and the set of buses
too old to keep, then write your rows, each with its quantifier and a label, before you code them.

The tests fix every `y[bid, option]` through its bounds and ask the solver whether the model accepts
the plan, so any correct formulation passes. About eight lines.
