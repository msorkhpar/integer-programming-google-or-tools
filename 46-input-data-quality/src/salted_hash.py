"""Lesson 12.2.3: hash() is salted per process for str; a hashlib digest of bytes is not.

Each line comes from a fresh Python process with a fixed PYTHONHASHSEED, standing in for two
service workers that each drew their own salt. GridCap is a fictional utility.
"""

import os
import subprocess
import sys

CHILD = """
import hashlib, json
key = ("P017", 2030)
text = json.dumps({"project_id": "P017", "start": 2030}, sort_keys=True)
print("hash(('P017', 2030))  ", hash(key))
print("hash(text)            ", hash(text))
print("hash(2030)            ", hash(2030))
print("sha256(text)[:16]     ", hashlib.sha256(text.encode("utf-8")).hexdigest()[:16])
"""

for seed in ("1", "2"):
    out = subprocess.run([sys.executable, "-c", CHILD], env={**os.environ, "PYTHONHASHSEED": seed},
                         capture_output=True, text=True, check=True).stdout
    print(f"process with PYTHONHASHSEED={seed}")
    print("".join("  " + line + "\n" for line in out.splitlines()), end="")

print("hash(-1) == hash(-2):", hash(-1) == hash(-2), f"(both {hash(-2)})")
