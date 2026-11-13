"""The benchmark's instance set: GridCap selection models, built once per solver API (module 22).

An instance is one program's slice of a GridCap medium portfolio: that program's projects, a child
kept only when its parent is in the same program, and each year's budget scaled to the slice's share
of the whole portfolio's spend in that year. Three programs times a few portfolio seeds give a set of
models that differ in size and difficulty but share one formulation. GridCap is fictional.

The same formulation is built three ways, because the solvers are reached through three APIs:
MathOpt (HiGHS and SCIP), CP-SAT's own `cp_model` (so that its deterministic time can be read), and
the linear solver wrapper `pywraplp` (CBC, which MathOpt does not have).
"""

from __future__ import annotations

from dataclasses import dataclass

from ortools.linear_solver import pywraplp
from ortools.math_opt.python import mathopt
from ortools.sat.python import cp_model

from gridcap import PROGRAMS, Project, generate

PORTFOLIO_SEEDS = (2027, 1)


@dataclass(frozen=True)
class Instance:
    name: str
    projects: tuple[Project, ...]
    years: tuple[int, ...]
    budget: dict[int, int]                      # $k per year

    def spend(self, p: Project, y: int) -> int:
        """What project p spends in year y if it starts at its earliest start ($k)."""
        return p.spend(p.earliest_start).get(y, 0)

    def groups(self) -> dict[str, list[str]]:
        """Alternative groups with at least two members in this instance."""
        found: dict[str, list[str]] = {}
        for p in self.projects:
            if p.alt_group:
                found.setdefault(p.alt_group, []).append(p.project_id)
        return {g: m for g, m in found.items() if len(m) > 1}

    def children(self) -> list[Project]:
        return [p for p in self.projects if p.parent]


def slices(portfolio_seed: int) -> list[Instance]:
    """One instance per program of the GridCap medium portfolio drawn with this seed."""
    pf = generate("medium", portfolio_seed)
    total = {y: sum(p.spend(p.earliest_start).get(y, 0) for p in pf.projects) for y in pf.years}
    found = []
    for program in PROGRAMS:
        projects = tuple(p for p in pf.projects if p.program == program
                         and (p.parent is None or pf.project(p.parent).program == program))
        share = {y: sum(p.spend(p.earliest_start).get(y, 0) for p in projects) for y in pf.years}
        budget = {y: pf.budget[y] * share[y] // max(total[y], 1) for y in pf.years}
        found.append(Instance(f"{program}-{portfolio_seed}", projects, pf.years, budget))
    return found


def instance_set() -> list[Instance]:
    return [inst for seed in PORTFOLIO_SEEDS for inst in slices(seed)]


def build_mathopt(inst: Instance) -> tuple[mathopt.Model, dict[str, mathopt.Variable]]:
    model = mathopt.Model(name=inst.name)
    x = {p.project_id: model.add_binary_variable(name=f"x_{p.project_id}") for p in inst.projects}
    for p in inst.projects:
        if p.must_do:
            model.add_linear_constraint(x[p.project_id] == 1, name=f"must_{p.project_id}")
    for g, members in inst.groups().items():
        model.add_linear_constraint(sum(x[i] for i in members) <= 1, name=f"alt_{g}")
    for c in inst.children():
        model.add_linear_constraint(x[c.project_id] <= x[c.parent], name=f"needs_{c.project_id}")
    for y in inst.years:
        model.add_linear_constraint(
            sum(inst.spend(p, y) * x[p.project_id] for p in inst.projects) <= inst.budget[y],
            name=f"budget_{y}")
    model.maximize(sum(p.value * x[p.project_id] for p in inst.projects))
    return model, x


def build_cpsat(inst: Instance) -> tuple[cp_model.CpModel, dict[str, cp_model.IntVar]]:
    model = cp_model.CpModel()
    x = {p.project_id: model.new_bool_var(f"x_{p.project_id}") for p in inst.projects}
    for p in inst.projects:
        if p.must_do:
            model.add(x[p.project_id] == 1)
    for members in inst.groups().values():
        model.add(sum(x[i] for i in members) <= 1)
    for c in inst.children():
        model.add(x[c.project_id] <= x[c.parent])
    for y in inst.years:
        model.add(sum(inst.spend(p, y) * x[p.project_id] for p in inst.projects) <= inst.budget[y])
    model.maximize(sum(p.value * x[p.project_id] for p in inst.projects))
    return model, x


def build_wrapper(inst: Instance, solver_id: str) -> tuple[pywraplp.Solver, dict]:
    solver = pywraplp.Solver.CreateSolver(solver_id)
    x = {p.project_id: solver.BoolVar(f"x_{p.project_id}") for p in inst.projects}
    for p in inst.projects:
        if p.must_do:
            solver.Add(x[p.project_id] == 1, f"must_{p.project_id}")
    for g, members in inst.groups().items():
        solver.Add(sum(x[i] for i in members) <= 1, f"alt_{g}")
    for c in inst.children():
        solver.Add(x[c.project_id] <= x[c.parent], f"needs_{c.project_id}")
    for y in inst.years:
        solver.Add(sum(inst.spend(p, y) * x[p.project_id] for p in inst.projects) <= inst.budget[y],
                   f"budget_{y}")
    solver.Maximize(sum(p.value * x[p.project_id] for p in inst.projects))
    return solver, x
