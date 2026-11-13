"""Lesson 10.2.4: what makes the digest of a snapshot change, and what must not.

A snapshot is the model's inputs written out in one canonical form; its digest (sha256) names it.
GridCap is a fictional utility's portfolio.
"""

import hashlib
import json
import os
import subprocess
import sys
from dataclasses import replace

from gridcap import generate


def digest(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:12]


a = {"budget": {"2027": 8890, "2028": 8120}, "force_in": ["P024"]}
b = {"force_in": ["P024"], "budget": {"2028": 8120, "2027": 8890}}          # same inputs, built in another order
print("insertion order, json.dumps          ", digest(json.dumps(a)), digest(json.dumps(b)))
print("insertion order, sort_keys=True      ", digest(json.dumps(a, sort_keys=True)), digest(json.dumps(b, sort_keys=True)))
print("insertion order, str()               ", digest(str(a)), digest(str(b)))

try:
    json.dumps({"force_in": {"P024", "P031"}})
except TypeError as error:
    print("a set in the inputs                  ", error)

CHILD = 'import hashlib; print(hashlib.sha256(str({"P024", "P031", "P007"}).encode()).hexdigest()[:12])'
for seed in ["1", "2"]:
    out = subprocess.run([sys.executable, "-c", CHILD], env={**os.environ, "PYTHONHASHSEED": seed},
                         capture_output=True, text=True, check=True).stdout.strip()
    print(f"{'str(set) digested, hash seed ' + seed:<37}", out)
print("sorted(set) digested                 ", digest(json.dumps(sorted({"P024", "P031", "P007"}))))

print("0.1 + 0.2 and 0.3 as JSON            ", json.dumps(0.1 + 0.2), json.dumps(0.3))
print("int key 2027 and str key '2027'      ", json.dumps({2027: 1}) == json.dumps({"2027": 1}))

small = generate("small")
cut = replace(small, budget={**small.budget, 2029: small.budget[2029] - 1})
print("GridCap small content hash           ", small.content_hash()[:12])
print("same, rebuilt from the generator     ", generate("small").content_hash()[:12])
print("2029 budget $1k lower                ", cut.content_hash()[:12])
