"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")

from harness import benchmark

# (solver, instance, seed) -> (solved, work units)
work = {
    ("Lynx", "yard-1", 3): (True, 250.0), ("Lynx", "yard-2", 3): (True, 4000.0),
    ("Lynx", "yard-1", 4): (True, 300.0), ("Lynx", "yard-2", 4): (True, 3600.0),
    ("Puma", "yard-1", 3): (True, 600.0), ("Puma", "yard-2", 3): (False, 90000.0),
    ("Puma", "yard-1", 4): (True, 650.0), ("Puma", "yard-2", 4): (True, 1500.0),
}
result = benchmark(lambda s, i, k: work[s, i, k], ["Lynx", "Puma"], ["yard-1", "yard-2"], [3, 4], 100.0, 1e5)
for solver, row in result.items():
    print(f"{solver}: runs {row['runs']}, solved {row['solved']}, repeat {row['repeat']}, sgm {round(row['sgm'], 1)}")
