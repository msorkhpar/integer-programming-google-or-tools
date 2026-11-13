"""Lesson 5.3.4: what gurobipy says when it finds no usable license, with the machine's details masked.

Each case runs in a child process with its own environment variables, so the result does not depend
on the license this machine has. The child prints only Gurobi's error number and the masked message:
the raw message names the user and the host, and that never reaches the output.
"""

import os
import subprocess
import sys
import tempfile

CHILD = r"""
import sys
import gurobipy as gp
from grb import mask
params = eval(sys.argv[1])
try:
    env = gp.Env(empty=True)
    env.setParam("OutputFlag", 0)
    for name, value in params.items():
        env.setParam(name, value)
    env.start()
    print("started")
except gp.GurobiError as error:
    print("GurobiError", error.errno, mask(str(error)))
"""

with tempfile.TemporaryDirectory() as empty_home:
    base = {k: v for k, v in os.environ.items() if k != "GRB_LICENSE_FILE"}
    base["HOME"] = empty_home                     # Gurobi also looks in the home directory
    cases = [
        ("no license anywhere", base, {}),
        ("GRB_LICENSE_FILE to a missing file", {**base, "GRB_LICENSE_FILE": "/licenses/missing.lic"}, {}),
    ]
    for label, env, params in cases:
        done = subprocess.run([sys.executable, "-c", CHILD, repr(params)], env=env, capture_output=True, text=True)
        print(f"{label}:\n  {done.stdout.strip()}")
