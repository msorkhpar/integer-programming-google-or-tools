A storm-response team (not GridCap) rents identical mobile units for the season. Each outage site
needs one unit for a number of days, a unit serves its sites one after another, and each unit is
rented for 30 days. `build` in `fleet.py` already has the model: $`x_{s,k} = 1`$ if site $`s`$ is
served by unit $`k`$, $`y_k = 1`$ if unit $`k`$ is rented, and

```math
\begin{aligned}
\min \;& \sum_k y_k \\
\text{s.t. }& \sum_k x_{s,k} = 1 && \forall s && \text{(served}_s) \\
& \sum_s d_s\, x_{s,k} \le 30\, y_k && \forall k && \text{(rental}_k)
\end{aligned}
```

Renumbering the units gives the same plan, so every plan appears many times. Write
`add_symmetry_breaking(fleet, days, units)`: rows that refuse every numbering that breaks one of
these two rules:

- the rented units are the first ones (no unit is rented while a lower-numbered one is not), and
- the sites, taken in the order the dict `days` lists them (its key order, as given, not sorted by
  their number of days), fill the units in order: site number $`n`$ (from 0) may only use units
  $`0, \dots, n`$. `fleet.py`'s own 14 sites happen to be listed longest first; one test's sites
  are not.

Unlike the lesson's crews, here a unit can stay unrented, so decide what the first rule means as a
row on the $`y`$. Before coding, write both families with their labels and argue on paper that every
plan can be renumbered to satisfy both at once, so the fewest units cannot change. Check the second
family on the first site: which units may it use?

Then run `fleet.py`: it solves the same 14 sites with and without your rows and prints HiGHS's node
counts. Write down both. The lesson found that ordering rows can cost nodes as well as save them;
see which happens here.

The tests fix whole plans and ask whether each is allowed, so any rows that keep this numbering pass.
About six lines.
