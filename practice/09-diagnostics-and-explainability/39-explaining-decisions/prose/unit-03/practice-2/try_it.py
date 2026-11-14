"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")

from swaps import pair_swaps

groups = {"line_P1": "pipe_1", "swap_P1": "pipe_1", "line_P5": "pipe_5", "swap_P5": "pipe_5"}

print("added line_P1 + gate_G8, dropped swap_P1:", pair_swaps(["line_P1", "gate_G8"], ["swap_P1"], groups))
print("added gate_G8, dropped swap_P5 + tank_T3:", pair_swaps(["gate_G8"], ["swap_P5", "tank_T3"], groups))
print("added line_P5 + swap_P1, dropped swap_P5 + line_P1:",
      pair_swaps(["line_P5", "swap_P1"], ["swap_P5", "line_P1"], groups))
