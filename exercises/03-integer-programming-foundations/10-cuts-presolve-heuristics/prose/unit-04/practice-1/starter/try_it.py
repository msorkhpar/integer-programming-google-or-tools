"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")

from rows import parse_row

# Lines copied from an imagined HiGHS log.
lines = {
    "row with source F": " F       3       1         2  10.00%   2410.75         2350               2.58%       12      4      1       210     0.3s",
    "periodic row": "        40       6        18  62.50%   2390.0          2380               0.42%       88      9     17      2600     1.2s",
    "row before the first LP": " u       0       0         0   0.00%   inf             1800               Large        0      0      0         0     0.0s",
    "a summary line": "  Primal bound       2380",
}

for label, line in lines.items():
    print(label + ":", parse_row(line))
