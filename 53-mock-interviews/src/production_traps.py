"""Mock 5's trap about tie-breaking weights: `hash()` against a `hashlib` digest, in fresh processes.

Each process gets its own string-hash seed, as two runs of a service would (lessons 10.2.3 and
12.2.3). The seeds are set here, 1 and 2, so the program prints the same lines every time it runs;
an unset seed is drawn at random for each process.
"""

from __future__ import annotations

import os
import subprocess
import sys

IDS = ["P017", "P032", "P101"]

CHILD = """
import hashlib, sys
ids = sys.argv[1:]
salted = [hash(i) % 100 for i in ids]
stable = [int(hashlib.sha256(i.encode()).hexdigest()[:8], 16) % 100 for i in ids]
print(" ".join(map(str, salted)), "|", " ".join(map(str, stable)))
"""


def weights_in_a_fresh_process(seed: str) -> tuple[str, str]:
    env = {**os.environ, "PYTHONHASHSEED": seed}
    done = subprocess.run([sys.executable, "-c", CHILD, *IDS], env=env, capture_output=True, text=True, check=True)
    salted, stable = done.stdout.strip().split(" | ")
    return salted, stable


def main() -> None:
    print(f"tie-break ranks (x % 100) for {', '.join(IDS)}")
    print(f"  {'process':<22} {'hash()':<12} sha256")
    for seed in ("1", "2"):
        salted, stable = weights_in_a_fresh_process(seed)
        print(f"  {'PYTHONHASHSEED=' + seed:<22} {salted:<12} {stable}")


if __name__ == "__main__":
    main()
