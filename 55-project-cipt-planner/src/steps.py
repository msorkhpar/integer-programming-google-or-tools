"""Load one snapshot of the CIPT planner (steps/NN) as the package `cipt`.

Every snapshot names its package `cipt`, so loading another one first forgets the modules of the
one before. The lesson programs use this to run the planner as it was after each lesson.
"""

from __future__ import annotations

import importlib
import sys
from pathlib import Path

STEPS = Path(__file__).resolve().parents[1] / "steps"


def use(step: int):
    """Import steps/NN/cipt and its submodules; return the package."""
    for name in [m for m in sys.modules if m == "cipt" or m.startswith("cipt.")]:
        del sys.modules[name]
    root = str(STEPS / f"{step:02d}")
    sys.path[:] = [p for p in sys.path if not p.startswith(str(STEPS))]
    sys.path.insert(0, root)
    package = importlib.import_module("cipt")
    for path in sorted((STEPS / f"{step:02d}" / "cipt").glob("*.py")):
        if path.stem not in ("__init__", "__main__"):
            setattr(package, path.stem, importlib.import_module(f"cipt.{path.stem}"))
    return package
