"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")
from hypothesis import Phase, given, settings

from drawn_properties import check, holds, portfolios

drawn = []


def tally(skip=frozenset(), examples=25):
    """How many of `examples` drawn portfolios keep every property, with `skip` planted in the model."""
    kept = []

    @settings(max_examples=examples, derandomize=True, database=None, deadline=None,
              phases=(Phase.generate,))
    @given(portfolios(max_projects=4))
    def run(case):
        drawn.append(case)
        try:
            holds(*case, skip=skip)
            kept.append(True)
        except AssertionError:
            kept.append(False)
    run()
    return f"{sum(kept)} of {len(kept)}"


print("properties kept, full model:", tally())
snapshot, witness = max(drawn, key=lambda case: len(case[1]))
print("a drawn portfolio's projects:", sorted(snapshot["projects"]), "budget:", snapshot["budget"])
print("its witness:", witness, "breaks:", check(snapshot, witness))
print("properties kept, no budget rows:", tally(frozenset({"budget"})))
print("properties kept, every lag read as 0:", tally(frozenset({"lag"})))
