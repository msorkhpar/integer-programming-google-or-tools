"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")

from sites import assign

crews = ["Fir", "Hazel", "Larch", "Rowan"]
sites = ["bridge", "quarry", "tunnel"]
cost = {("Fir", "bridge"): 6, ("Fir", "quarry"): 3, ("Fir", "tunnel"): 9,
        ("Hazel", "bridge"): 4, ("Hazel", "quarry"): 7, ("Hazel", "tunnel"): 5,
        ("Larch", "bridge"): 8, ("Larch", "quarry"): 2, ("Larch", "tunnel"): 6,
        ("Rowan", "bridge"): 5, ("Rowan", "quarry"): 6, ("Rowan", "tunnel"): 4}
print("four crews, three sites:", assign(crews, sites, cost))
no_tunnel = {pair: c for pair, c in cost.items() if pair[1] != "tunnel" or pair[0] == "Fir"}
print("only Fir may take the tunnel:", assign(crews, sites, no_tunnel))
only_fir = {pair: c for pair, c in cost.items() if pair[0] == "Fir"}
print("only Fir has any pairs:", assign(crews, sites, only_fir))
