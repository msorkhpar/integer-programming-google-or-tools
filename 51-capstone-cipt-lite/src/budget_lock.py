"""Lesson 13.1.4: the Budget Lock scenario on GridCap medium, explained in one planner message.

Finance locks the 2028 budget at $40,000k, and a contractor change leaves 18 transmission
crew-months in each of 2029 and 2030. The model is infeasible; the message says why. A second
scenario, with a 2027 budget typed far too low, is stopped by the pre-solve checks before any
filter runs. GridCap is a fictional utility's portfolio.
"""

from __future__ import annotations

from cipt_diagnose import message, presolve_checks
from cipt_model import Scenario, build, params, solve
from gridcap import generate

LOCK = Scenario(name="budget-lock", budget={2028: 40_000},
                crews={("transmission", 2029): 18, ("transmission", 2030): 18})
TYPO = Scenario(name="budget-lock-typo", budget={2027: 428})

if __name__ == "__main__":
    medium = generate("medium")
    b = build(medium, LOCK)
    run = solve(b.model, params(gap=1e-3))
    print(f"solve: {run.termination.reason.name}; pre-solve findings: {len(presolve_checks(medium, LOCK))}")
    print()
    print(message(b))
    print()
    print(message(build(medium, TYPO)))
