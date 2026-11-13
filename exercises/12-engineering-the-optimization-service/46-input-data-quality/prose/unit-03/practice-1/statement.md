A water utility's inspection team sends pipe surveys to a planning service, and both teams must be
able to name a survey by its digest: the same survey content gives the same digest on either side,
whatever order the keys or records arrive in. A survey has scalar fields, a list of `tags`, and a
list of `segments`, each with an `id`, a `material`, a length and a list of wall-thickness
`readings` taken in order along the pipe.

In `survey.py`, write `digest(doc)`: the SHA-256 hex digest of the survey's canonical bytes, defined
by both teams as follows.

- The records of `segments` are in `id` order, and `tags` are sorted. These are the lists named in
  `UNORDERED`. The rule goes by the key a list sits under, at any depth: a list held under a key
  named in `UNORDERED`, in any object of the document, is sorted the same way. Every other list,
  `readings` included, keeps its order.
- Every float is cut to 3 decimals by fixed-point formatting, so `0.1 + 0.2` and `0.3` agree; `-0.0`
  becomes `0.0`; a NaN or an infinity raises `ValueError`.
- The bytes are `json.dumps` of the result with sorted keys, separators `(",", ":")`,
  `ensure_ascii=True` and `allow_nan=False`, encoded as ASCII.

One segment's material is written with a non-ASCII letter, so the last rule matters: the other team
has pinned the digest of the test survey, and only exactly these bytes give it. About twenty lines.
