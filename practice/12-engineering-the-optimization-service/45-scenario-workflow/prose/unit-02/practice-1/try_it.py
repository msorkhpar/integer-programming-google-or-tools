"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")

from overrides import bounds_for

window = range(2033, 2037)   # 2033 to 2036

print("start_in 2035:", bounds_for("start_in", (2035,), window))
print("only_between 2034-2035:", bounds_for("only_between", (2034, 2035), window))
print("skip_years 2033, 2036:", bounds_for("skip_years", (2033, 2036), window))
print("only_between 2040-2041:", bounds_for("only_between", (2040, 2041), window))
