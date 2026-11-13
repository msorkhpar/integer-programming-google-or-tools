"""Build lesson 6.4.1's model in PuLP on GridCap tiny and read the LP file PuLP writes for it."""

import tempfile
from pathlib import Path

import pulp

from gridcap import generate
from pulp_timing import build

tiny = generate("tiny")
pt = build(tiny)
print(f"{pt.prob.name}: {pt.prob.numVariables()} variables, {pt.prob.numConstraints()} rows,",
      "maximize" if pt.prob.sense == pulp.LpMaximize else "minimize", pt.prob.objective.name)
print("row names:", ", ".join(row.name for row in pt.prob.constraints()))

with tempfile.TemporaryDirectory() as folder:
    path = Path(folder) / "gridcap_tiny.lp"
    pt.prob.writeLP(str(path))
    text = path.read_text()
lines = text.splitlines()
print(f"--- gridcap_tiny.lp ({len(lines)} lines), up to the first budget row:")
for line in lines[: lines.index("Subject To") + 5]:
    print(line)
print("...")
print("rows in the file, in order:", ", ".join(line.split(":")[0] for line in lines if line[:1].isalpha() and ":" in line))
