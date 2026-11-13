"""Lesson 10.2.4: which solver a run used is decided by package versions, so record and check them.

OR-Tools' wheel carries its own HiGHS and SCIP libraries, so the OR-Tools version pins the HiGHS and
SCIP that MathOpt runs; the `highspy` package is a separate build of HiGHS.
"""

import glob
import os
from importlib.metadata import version

import ortools


def check_pins(pins: dict[str, str]) -> list[str]:
    """Every package whose installed version is not the pinned one, as 'name: pinned X, found Y'."""
    return [f"{name}: pinned {want}, found {version(name)}"
            for name, want in sorted(pins.items()) if version(name) != want]


if __name__ == "__main__":
    libs = sorted(os.path.basename(p) for p in glob.glob(os.path.join(os.path.dirname(ortools.__file__), ".libs", "*"))
                  if any(s in os.path.basename(p) for s in ("highs", "scip", "ortools")))
    print("ortools", version("ortools"), "carries:", ", ".join(libs))
    print("highspy", version("highspy"), "(HiGHS packaged on its own, apart from the copy in the OR-Tools wheel)")
    print("pins as installed:", check_pins({"ortools": "9.15.6755", "highspy": "1.14.0"}) or "all match")
    print("a stale pin:      ", check_pins({"ortools": "9.14.6206"}))
