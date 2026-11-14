"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")

from invoices import fits

print("0.15 + 0.15 within 0.30:", fits([0.15, 0.15], 0.30))
print("0.7 + 0.1 within 0.8:", fits([0.7, 0.1], 0.8))
print("19.99 + 0.02 within 20.00:", fits([19.99, 0.02], 20.00))
print("0.33 * 3 within 0.99:", fits([0.33, 0.33, 0.33], 0.99))
