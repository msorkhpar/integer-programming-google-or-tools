"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")

from claims import judge_claim

# A maximization at incumbent 7,400 and bound 7,650.
for claim in (7_000, 7_500, 7_650, 7_700):
    print(f"claim {claim}, max, bracket 7400..7650:", judge_claim(claim, incumbent=7_400, bound=7_650, maximize=True))
print("claim 1200, min, bracket 1100..1300:", judge_claim(1_200, incumbent=1_300, bound=1_100, maximize=False))
print("claim 50, max, no incumbent, bound 7650:", judge_claim(50, incumbent=None, bound=7_650, maximize=True))
