A water utility's scenario diff lists the mains it adds and drops between two runs. Many mains have
two options in an alternative group, reline or replace, and at most one option per group is funded.
When a diff shows `replace_M4` dropped and `reline_M4` added, the asset managers read it as one
decision, "reline main 4 instead of replacing it", and they want the report to say so.

In `swaps.py`, write `pair_swaps(adds, drops, group_of)`. `adds` and `drops` are the diff's two
lists; `group_of` maps a project to its alternative group, and a project with no group is absent.
Return a dictionary:

- `"swaps"`: a list of `(dropped, added)` pairs, one per dropped project whose group gained an added
  project, sorted by the dropped id;
- `"adds"` and `"drops"`: what is left of each list once the swapped projects are taken out, sorted.

Because each group keeps $`\sum_{i \in g} \text{started}(i) \le 1`$ in both plans, a group can lose at
most one option and gain at most one. Before coding, write down what that row implies about how many
swaps one group can produce, and what a project with no group can be paired with. The tests use
their own mains.
