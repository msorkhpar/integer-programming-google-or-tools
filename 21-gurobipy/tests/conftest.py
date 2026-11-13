import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SRC = Path(__file__).resolve().parents[1] / "src"
# This module's programs first; then the MathOpt models of lessons 4.2.1 (module 13) and 6.4.1 /
# 4.3.x (module 14), which the tests solve next to their gurobipy ports. Their file names do not clash.
for path in (SRC, ROOT / "13-mathopt-core" / "src", ROOT / "14-mathopt-advanced" / "src"):
    if str(path) not in sys.path:
        sys.path.append(str(path))
