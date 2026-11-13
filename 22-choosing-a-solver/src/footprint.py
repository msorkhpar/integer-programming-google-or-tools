"""What each solver package in the runner image declares as its license, and what it weighs on disk (lesson 5.4.3).

Read from the installed packages' own metadata, so the answer is the one pip saw. The runner is an
offline container (`docker run --network none`), so every solver that solves here needs no network
and no license server.
"""

from __future__ import annotations

import importlib.metadata as md


def declared_license(meta) -> str:
    """The License-Expression field if present, else the License field, else the trove classifiers."""
    if meta.get("License-Expression"):
        return meta["License-Expression"]
    if meta.get("License"):
        return meta["License"].strip()
    found = [c.split(" :: ")[-1] for c in meta.get_all("Classifier") or [] if c.startswith("License ::")]
    return ", ".join(found) or "(none declared)"


print(f"{'package':<10} {'version':<10} {'declared license':<24} {'installed size':>14}  solvers inside")
for package, inside in (("ortools", "GLOP, PDLP, CP-SAT, and builds of HiGHS, SCIP, CBC, CLP"),
                        ("highspy", "HiGHS"),
                        ("PuLP", "a CBC executable per platform"),
                        ("gurobipy", "Gurobi (needs a license to solve beyond its limits)")):
    dist = md.distribution(package)
    size = sum(f.size or 0 for f in dist.files or [])
    print(f"{package:<10} {dist.version:<10} {declared_license(dist.metadata):<24} {size / 1e6:>11.1f} MB  {inside}")

for package in ("pyscipopt", "xpress", "cplex"):
    try:
        md.distribution(package)
        print(f"{package}: installed")
    except md.PackageNotFoundError:
        print(f"{package}: not in the runner image")
