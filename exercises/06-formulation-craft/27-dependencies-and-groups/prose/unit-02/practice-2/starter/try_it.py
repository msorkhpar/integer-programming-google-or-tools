"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")
from entry import Project, entry_cost, implied_required

# HALL needs ROOF and WALLS; ROOF needs WALLS; WALLS needs SITE. FENCE needs GATE.
works = {
    "SITE": Project(500),
    "WALLS": Project(250, ("SITE",)),
    "ROOF": Project(120, ("WALLS",)),
    "HALL": Project(80, ("ROOF", "WALLS")),
    "GATE": Project(15),
    "FENCE": Project(35, ("GATE",)),
}

print("entry cost of GATE:", entry_cost(works, "GATE"))
print("entry cost of FENCE:", entry_cost(works, "FENCE"))
print("entry cost of HALL:", entry_cost(works, "HALL"))
print("implied by {ROOF}:", sorted(implied_required(works, {"ROOF"})))
print("implied by {FENCE, SITE}:", sorted(implied_required(works, {"FENCE", "SITE"})))
