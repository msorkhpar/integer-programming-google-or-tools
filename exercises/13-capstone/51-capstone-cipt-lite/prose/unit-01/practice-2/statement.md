The practice portfolio has passed milestone 1's reader. Every later run must now say *which* inputs
it solved, in a way any worker can check on any day: by a digest of the snapshot's content. Two
exports of the same content must get the same name, and any real change, however small, a new one.

The snapshot is the practice series' format: nested dictionaries keyed by year, region, program or
project id, lists that carry their order (`years`, each `cost` profile, spent year by year), ints for
money, and one float, `rate`.

In `snapshot.py`, write:

| function | contract | lesson |
| --- | --- | --- |
| `fixed(value)` | the float cut to `PLACES` (6) decimals by fixed formatting, `-0.0` as `0.0`; `ValueError` for NaN or infinity | 12.2.3 |
| `canonical(snap)` | the snapshot as bytes: every float through `fixed`, every list in its own order, keys sorted at every level, separators `","` and `":"` with no spaces, ASCII only, NaN refused | 10.2.4, 12.2.3 |
| `name(data)` | the SHA-256 of the bytes as 64 hex digits, the same in every process | 12.2.3 |
| `digest(snap)` | `name(canonical(snap))` | 12.2.3 |
| `Store(root).put(snap)` | write the canonical bytes to `<digest>.json` only if that file does not exist yet; return the digest | 12.2.3 |
| `Store(root).get(key)` | read `<key>.json`, re-hash it, raise `Edited` if the bytes no longer hash to `key`, else return the parsed JSON | 12.2.3 |

The documented byte form is what `json.dumps(..., sort_keys=True, separators=(",", ":"),
ensure_ascii=True, allow_nan=False)` writes: the planning team pinned the digest of their test
snapshot from it, and your digest must match theirs byte for byte. Dictionaries in another order are
the same content; a reversed cost profile is not. About thirty-five lines.
