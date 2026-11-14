"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")

from limits import limits_for


def request(**given):
    return {"matters_dollars": None, "share_percent": None, "minutes": None, "nodes": None, **given}


def show(label, p):
    print(label, "abs", p.absolute_gap_tolerance, "rel", p.relative_gap_tolerance,
          "nodes", p.node_limit, "time", p.time_limit)


show("$25,000, 2 percent, 15 min:", limits_for(request(matters_dollars=25_000, share_percent=2, minutes=15)))
show("1.5 min only:", limits_for(request(minutes=1.5)))
show("0.2 percent, 45 min, 8000 nodes:", limits_for(request(share_percent=0.2, minutes=45, nodes=8_000)))
