"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")

from scaling import scale_row

print("0.75 x + 1.2 y <= 5.1:", scale_row(["0.75", "1.2"], "5.1", "<="))
print("2.5 x + 0.4 y >= 3.3:", scale_row(["2.5", "0.4"], "3.3", ">="))
print("0.5 x + 1.5 y == 2:", scale_row(["0.5", "1.5"], "2", "=="))
print("0.5 x + 1.5 y == 2.25:", scale_row(["0.5", "1.5"], "2.25", "=="))
print("3 x + 4 y <= 10:", scale_row(["3", "4"], "10", "<="))
