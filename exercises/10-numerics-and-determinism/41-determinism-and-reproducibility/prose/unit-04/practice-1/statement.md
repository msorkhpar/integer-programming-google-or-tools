A transmission planner keeps every scenario's inputs in a dict such as

```python
{"budget": {"2027": 4200, "2028": 3900}, "force_in": {"T-07", "T-11"}, "gap": 0.0}
```

where `force_in` is a Python set of line ids. Each scenario is named by the sha256 digest of its
inputs, so a rerun can prove it used exactly the same ones.

Write `snapshot_digest(inputs)` that returns the 64-character hex digest. Equal inputs must give the
same digest whatever order their dicts were built in and in any Python process; a changed number or
string, or an item added to or removed from a list or set, must give a different digest. Inputs hold
dicts with string keys, lists, sets of strings, strings and numbers, nested to any depth.

The canonical form, as in the lesson, is JSON with sorted keys and each set written as its sorted
list. That form does not tell every pair of inputs apart, and the tests don't ask it to: a set and
a list holding the same items in sorted order give the same digest, and so would a dict keyed by the
number 2027 and one keyed by the string `"2027"`, since JSON writes every key as a string. That is
why keys must be strings and a field must always hold the same kind of value.

About eight lines.
