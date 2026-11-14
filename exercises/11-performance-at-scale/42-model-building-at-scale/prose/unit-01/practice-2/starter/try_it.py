"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")

from growth import fit, predict

sizes = [500, 1_000, 2_000, 4_000]
cubic = [2e-9 * n ** 3 for n in sizes]
a, c = fit(sizes, cubic)
print("exponent, times 2e-9 * n^3:", round(a, 3))
print("constant, times 2e-9 * n^3:", f"{c:.3g}")
print("predicted seconds at 10,000:", round(predict(sizes, cubic, 10_000), 1))

measured = [0.4, 1.1, 2.9, 9.5]
print("exponent, measured times:", round(fit(sizes, measured)[0], 3))
print("predicted seconds at 10,000, measured:", round(predict(sizes, measured, 10_000), 1))
