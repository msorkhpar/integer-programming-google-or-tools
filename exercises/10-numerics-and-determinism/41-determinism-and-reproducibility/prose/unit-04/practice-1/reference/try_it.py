"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")

from scenario import snapshot_digest

inputs = {"budget": {"2031": 5100, "2032": 4800}, "force_in": {"P-3", "P-8", "P-1"},
          "settings": {"seed": 9, "solver": "highs"}}
rebuilt = {"settings": {"solver": "highs", "seed": 9}, "force_in": {"P-1", "P-3", "P-8"},
           "budget": {"2032": 4800, "2031": 5100}}

print("digest of the inputs:", snapshot_digest(inputs))
print("digest, same inputs built in another order:", snapshot_digest(rebuilt))
print("digest, 2032 budget 4700:", snapshot_digest({**inputs, "budget": {"2031": 5100, "2032": 4700}}))
