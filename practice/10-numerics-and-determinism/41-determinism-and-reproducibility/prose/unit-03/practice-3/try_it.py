"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")

from weights import separating_weights

print("weights for three sites:", separating_weights(["K-30", "K-07", "K-15"]))
print("same sites, other order:", separating_weights(["K-15", "K-30", "K-07"]))
print("weights for one site:", separating_weights(["K-99"]))
