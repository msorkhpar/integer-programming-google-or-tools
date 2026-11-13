A railway's maintenance planner reruns each night's plan and compares manifests. When two differ,
the on-call engineer needs to see exactly where. A manifest is nested dicts and lists, for example
`{"result": {"objective": 41.0, "plan": [["S1", 3], ["S4", 1]]}}`.

Write `diff_paths(a, b)`. It returns the sorted list of every path at which the two differ:

- dict keys are joined with dots: `"result.objective"`;
- a key present in only one of the two is a difference at that key's path;
- two lists of the same length are compared item by item, and an item's path ends in its index:
  `"result.plan[1]"`, or deeper, `"result.plan[1][0]"`;
- two lists of different lengths, or two values of different kinds, differ at their own path. The
  kinds are three: a dict, a list, or a plain value (a string, number, boolean or `None`). A dict
  against a list, or a list against a string, is a difference of kind.
- two plain values are compared with `==`, as the lesson's own diff does, so `41` and `41.0` are
  equal and give no path.

Equal manifests give `[]`. About fifteen lines.
