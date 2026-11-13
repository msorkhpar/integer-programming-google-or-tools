The transit agency's fleet export is read by another program, and two versions of it are in use.
Version 3, the current one, gives each bus an id, a `depot`, a `cost` in $k and a `must_replace`
flag (the model's $`\text{replace}_b`$ row is an equality only for such buses). Version 2, still sent
by one older depot system, called the depot `garage` and had no `must_replace` at all: in version 2
no replacement was mandatory.

In `contract.py`, make the schema a contract for documents sent by a program, and bring version 2
documents forward:

- `Contract` refuses keys the schema does not declare and refuses values in the wrong JSON type
  (a number sent as text, a flag sent as text), and its objects cannot be changed after loading.
- `Fleet` accepts version 3 only.
- `upgrade(raw)` turns a version 2 document into the version 3 document it means, and leaves any
  other document as it is, for the schema to accept or refuse. It must not drop keys it does not
  know: a key that is wrong in version 2 is still wrong after the upgrade. `depot` and
  `must_replace` are such keys: version 2 never had them, so a version 2 document whose buses carry
  either one (a `must_replace` flag, or a `depot` beside the `garage`) is left as it is, still at
  version 2, and the schema refuses it. Guessing which depot or flag was meant would hide the
  sender's mistake.

`parse(text)` is written; it returns `None` for any document the contract refuses. About ten lines.
