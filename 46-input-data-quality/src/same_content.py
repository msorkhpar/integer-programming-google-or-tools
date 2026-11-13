"""Lesson 12.2.3: hash the validated content in canonical form, not the file's bytes.

Two exports of the same GridCap small snapshot differ in key order, record order, layout and how
the discount rate was computed. GridCap is a fictional utility.
"""

import copy
import hashlib
import json
import os
import subprocess
import sys

from canonical import canonical, digest, fixed
from gridcap import generate
from snapshot import export, load


def short(data: str | bytes) -> str:
    return hashlib.sha256(data.encode("utf-8") if isinstance(data, str) else data).hexdigest()[:12]


doc = export(generate("small"))
first = json.dumps(doc)
other = copy.deepcopy(doc)
other["projects"].reverse()                                   # the database returned rows in another order
other["discount_rate"] = 0.7 / 10                             # computed, not typed: 0.06999999999999999
second = json.dumps(other, indent=2, sort_keys=True)          # pretty-printed, keys sorted

print(f"{'':<14} {'file bytes':<13} {'model_dump_json':<16} canonical")
for label, text in [("first export", first), ("second export", second)]:
    snap = load(text)
    print(f"{label:<14} {short(text):<13} {short(snap.model_dump_json()):<16} {digest(snap)[:12]}")

snap = load(first)
print("canonical bytes start:", canonical(snap)[:72].decode())
print("discount_rate in canonical form:", json.loads(canonical(load(second)))["discount_rate"])
print("fixed():", ", ".join(f"{v!r} -> {fixed(v)!r}" for v in (0.7 / 10, 0.1 + 0.2, -0.0)))

changed = copy.deepcopy(doc)
changed["budget"][2]["amount"] -= 1                           # 2029 budget $1k lower
swapped = copy.deepcopy(doc)
swapped["projects"][38]["cost_profile"].reverse()             # P039 spends 880 then 1,170
for label, d in [("2029 budget $1k lower", changed), ("P039 profile reversed", swapped)]:
    print(f"{label:<22} canonical {digest(load(json.dumps(d)))[:12]}")

CHILD = "import json,sys; from canonical import digest; from snapshot import load; " \
        "print(digest(load(sys.stdin.read())))"
for seed in ("1", "2"):
    out = subprocess.run([sys.executable, "-c", CHILD], input=first, capture_output=True, text=True, check=True,
                         env={**os.environ, "PYTHONHASHSEED": seed}).stdout.strip()
    print(f"canonical digest in a process with PYTHONHASHSEED={seed}: {out[:12]}")
