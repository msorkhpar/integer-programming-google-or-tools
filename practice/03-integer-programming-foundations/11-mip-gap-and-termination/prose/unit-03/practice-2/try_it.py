"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")

from fund_or_skip import fund_or_skip

print("in (720, 730), out (690, 710):", fund_or_skip(forced_in=(720, 730), forced_out=(690, 710)))
print("in (650, 660), out (700, 705):", fund_or_skip(forced_in=(650, 660), forced_out=(700, 705)))
print("in (700, 725), out (705, 715):", fund_or_skip(forced_in=(700, 725), forced_out=(705, 715)))
print("in (720, 730), out None:", fund_or_skip(forced_in=(720, 730), forced_out=None))
print("in None, out (690, 710):", fund_or_skip(forced_in=None, forced_out=(690, 710)))
