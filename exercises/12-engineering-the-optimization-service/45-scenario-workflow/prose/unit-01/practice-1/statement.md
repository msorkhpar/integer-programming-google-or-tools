A water utility, Riverbend Water (invented for this practice), keeps its pumping plans as records
like this one:

```python
{"id": "W-1", "name": "base", "owner": "analyst-a", "created": "2027-01-04T08:00Z",
 "demand": {"north": 41, "south": 37, "east": 12},
 "budget": {2027: 900, 2028: 950, 2029: 990},
 "settings": {"solver": "HIGHS", "gap": 0.0}}
```

Its run service must tell whether two plans were solved on the same inputs. The inputs are the
fields named in `INPUT_KEYS`: demand, budget and solver settings. Everything else (id, name, owner,
creation time) is metadata and must not affect the answer.

Write `snapshot(record)` in `snapshot.py`. It returns the sha256 hex digest of the record's inputs
only, written as text that is the same for the same inputs however their dictionaries were filled
in. Records in the tests may carry metadata keys you have not seen. Every record carries all three
input keys; one that lacks an input is malformed, and the reference lets it raise `KeyError` rather
than hash an incomplete plan (no test sends one). About four lines.
