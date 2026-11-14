"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")

from likelihood import log_likelihood

failed = [9.0, 17.0, 26.0]
working = [20.0, 28.0]

print("beta 2, eta 25, failures only:", round(log_likelihood(2.0, 25.0, failed, []), 4))
print("beta 2, eta 25, with two still working:", round(log_likelihood(2.0, 25.0, failed, working), 4))
print("beta 2, eta 35, with two still working:", round(log_likelihood(2.0, 35.0, failed, working), 4))
