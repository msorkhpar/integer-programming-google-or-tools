"""A small automated tuner: try every combination of a few Gurobi parameters, score each on a training set.

A configuration is a dict of Gurobi parameters; `{}` is the default. A score is the shifted geometric
mean, over the training instances, of the work to prove optimality (Gurobi's deterministic work, in
thousandths of a unit, shift 10), so a score repeats exactly and two scores compare fairly.
"""

from __future__ import annotations

import itertools

import gurobipy as gp
from gurobipy import GRB

from gridcap import generate
from grb_runs import build_gurobi
from plan_model import REGIONS, region_portfolio
from sgm import shifted_geometric_mean

SHIFT = 10.0
#: The grid: every combination of these values; -1 is Gurobi's "automatic" (its default).
GRID = {"MIPFocus": (0, 1, 2), "Cuts": (-1, 0, 1), "Presolve": (-1, 1)}


def configurations() -> list[dict]:
    """Every combination of the grid, written with only the parameters it changes from the default."""
    found = []
    for values in itertools.product(*GRID.values()):
        changed = {k: v for k, v in zip(GRID, values) if v != GRID[k][0]}
        found.append(changed)
    return found


def label(config: dict) -> str:
    return " ".join(f"{k}={v}" for k, v in config.items()) or "default"


def tuning_set(portfolio_seeds=(2027, 1, 2, 3)) -> list:
    """Every region of the medium portfolios drawn with these seeds: 16 regional plans."""
    return [region_portfolio(generate("medium", s), r) for s in portfolio_seeds for r in REGIONS]


class Tunable:
    """One regional plan's Gurobi model, built once and re-solved under each configuration."""

    def __init__(self, env: gp.Env, pf) -> None:
        self.name = pf.name
        self.model, _ = build_gurobi(env, pf)

    def work(self, seed: int, config: dict) -> float:
        """Work to prove optimality, in thousandths of a Gurobi work unit."""
        m = self.model
        m.reset()                                  # forget the last solve, so no run starts from another
        m.Params.Threads, m.Params.Seed, m.Params.MIPGap = 1, seed, 0.0
        for name, values in GRID.items():
            m.setParam(name, config.get(name, values[0]))
        m.optimize()
        if m.Status != GRB.OPTIMAL:
            raise RuntimeError(f"{self.name} did not solve with {label(config)}")
        return m.Work * 1000


def score(table: dict, names: list[str], config: dict, seed: int = 1) -> float:
    """SGM of work over `names` for one configuration, from a table {(name, seed, label): work}."""
    return shifted_geometric_mean([table[n, seed, label(config)] for n in names], SHIFT)


def pick(table: dict, names: list[str], configs: list[dict], seed: int = 1) -> dict:
    """The configuration with the best score on `names`; ties go to the earlier one (the default first)."""
    return min(configs, key=lambda c: score(table, names, c, seed))
