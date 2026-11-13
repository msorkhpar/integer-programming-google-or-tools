"""The planner's command line on the demo export, as each step left it.

data/demo.json in every snapshot is GridCap tiny (8 projects, 3 years), a fictional utility's
portfolio written by export.py. Each run is `python -m cipt data/demo.json` inside steps/NN.
"""

import subprocess
import sys

from steps import STEPS

RUNS = [(0, []), (1, []), (2, []), (3, []), (4, []), (6, ["--why", "P003"])]

for step, extra in RUNS:
    print(f"$ python -m cipt data/demo.json {' '.join(extra)}".rstrip() + f"    # steps/{step:02d}")
    done = subprocess.run([sys.executable, "-m", "cipt", "data/demo.json", *extra], cwd=STEPS / f"{step:02d}",
                          capture_output=True, text=True)
    print(done.stdout.rstrip())
    print()
