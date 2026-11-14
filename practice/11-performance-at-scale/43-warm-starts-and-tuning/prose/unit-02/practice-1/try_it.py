"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")

from highs_log import incumbents

# A short HiGHS log for a depot schedule: header, then the progress table.
log = [
    "Presolving model",
    "Src  Proc. InQueue |  Leaves   Expl. | BestBound       BestSol              Gap |   Cuts   InLp Confl. | LpIters     Time",
    "         0       0         0   0.00%   0               inf                  inf        0      0      0         0     0.0s",
    " J       0       0         0   0.00%   0               5400               Large        0      0      0         0     0.0s",
    " L       0       0         0   0.00%   4810            5120               6.05%       10      6      0       133     0.1s",
    "         0       0         0   0.00%   4850            5120               5.27%       12      8      0       260     0.1s",
    " T      40       2        18  80.00%   4950            4990               0.80%       20     11     30      2048k    0.6s",
    "",
    "Solving report",
]

for lp_iterations, plan in incumbents(log):
    print(f"new plan {plan} after {lp_iterations} LP iterations")
print("as a maximization:", incumbents(log, minimize=False))
