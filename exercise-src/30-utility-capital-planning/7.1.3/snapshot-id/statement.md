A water utility (a fictional one) keeps its planning scenarios as JSON-ready dictionaries:
budgets, floors, the projects a planner forced in or out, and the solver settings. It wants a
**snapshot id** for each scenario, so that two runs can be compared by their ids, and a short
answer to "what is different between these two scenarios?".

Write two functions in `snapshot.py`:

- `snapshot_id(inputs)`: the sha256 hex digest of one **canonical text** of the inputs, encoded as
  UTF-8. The canonical text is the inputs written as JSON with every dictionary's keys sorted and
  no spaces (separators `","` and `":"`), and with the lists under `force_in` and `force_out`
  sorted, because they are sets of project ids. Two scenarios that differ only in the order their
  dictionaries were built, or the order of those id lists, must get the same id; any other change
  must give a different one.
- `changed_fields(a, b)`: the sorted top-level field names whose values differ between two
  scenarios, by the same canonical rules. A field that only one of them has is a change.

Two details of the canonical text. Only the top-level `force_in` and `force_out` lists are sorted; a
list of that name nested inside another field (say `settings`) is written in the order it has.
And the text is `json.dumps`'s output with its default `ensure_ascii=True`, so a character outside
ASCII is written as an escape: a region named `"Côte"` appears as `"C\u00f4te"`. The UTF-8 encoding
is then applied to that text.

Before you code, write the canonical text of `{"force_in": ["W2", "W1"], "budget": {"2028": 950,
"2027": 900}}` by hand. The tests compare your id with the digest of texts written out by hand.
About ten lines; Python's `json` and `hashlib` do the work.
