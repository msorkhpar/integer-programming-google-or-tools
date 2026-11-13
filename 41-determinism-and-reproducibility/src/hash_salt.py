"""Lesson 10.2.1: Python salts str hashes per process, so a set of project ids changes its order.

Each line comes from a fresh Python process started with a given PYTHONHASHSEED. With the seed
unset or "random" (the default), every process draws its own salt; the fixed seeds 1 and 2 stand in
for two such processes so the output can be shown.
"""

import os
import subprocess
import sys

CHILD = """
import hashlib
ids = ["P%03d" % i for i in range(1, 41)]
print("hash('P017') =", hash("P017"))
print("list(set(ids))[:5] =", list(set(ids))[:5])
print("sorted(set(ids))[:5] =", sorted(set(ids))[:5])
print("sha256('P017')[:12] =", hashlib.sha256(b"P017").hexdigest()[:12])
"""


def child(seed: str) -> list[str]:
    env = {**os.environ, "PYTHONHASHSEED": seed}
    return subprocess.run([sys.executable, "-c", CHILD], env=env, capture_output=True, text=True,
                          check=True).stdout.splitlines()


for seed in ["1", "2"]:
    print(f"PYTHONHASHSEED={seed}")
    for line in child(seed):
        print("  " + line)

salted = {child("random")[0] for _ in range(5)}
print(f"hash('P017') in 5 processes with a random salt: {len(salted)} different values")
