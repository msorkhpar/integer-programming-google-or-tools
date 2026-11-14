"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")
from speedup import crossover, speedups


def rec(solver, device, n, seconds, first=False, err=1e-9):
    return {"solver": solver, "device": device, "n": n, "seconds": seconds, "first_in_process": first, "rel_error": err}


records = [
    rec("simplex", "cpu", 200, 0.08), rec("pdlp", "gpu", 200, 0.30), rec("pdlp", "gpu", 200, 1.5, first=True),
    rec("simplex", "cpu", 2000, 4.0), rec("pdlp", "gpu", 2000, 1.6), rec("pdlp", "gpu", 2000, 2.0),
    rec("pdlp", "gpu", 2000, 9.0),
    rec("simplex", "cpu", 8000, 60.0), rec("pdlp", "gpu", 8000, 6.0), rec("fast", "gpu", 8000, 2.0, err=1e-4),
]
table = speedups(records, 1e-6)
print("speed-ups, needed 1e-6:", {n: None if s is None else round(s, 3) for n, s in table.items()})
print("crossover, needed 1e-6:", crossover(table))
loose = speedups(records, 1e-3)
print("speed-ups, needed 1e-3:", {n: None if s is None else round(s, 3) for n, s in loose.items()})
print("crossover of {50: 2.0, 500: 0.8, 5000: 3.0}:", crossover({50: 2.0, 500: 0.8, 5000: 3.0}))
