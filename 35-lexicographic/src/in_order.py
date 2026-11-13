"""Solve a MathOpt model's prioritized objectives one at a time (lesson 4.3.2's `in_order.py`).

Copied from module 14 so that this module runs on its own. `add_auxiliary` works around a bug: in
OR-Tools 9.15, `add_auxiliary_objective(expr=...)` erases the terms of every auxiliary objective
already in the model, so each one is created empty and its terms are set one at a time.
`solve_in_order` is what a hierarchical solver does, as the `ObjectiveParameters` docstring in
OR-Tools' `model_parameters.py` describes it.
"""

from __future__ import annotations

from ortools.math_opt.python import mathopt

from lex_model import quiet

EXACT = mathopt.SolveParameters(relative_gap_tolerance=0.0)


def add_auxiliary(model: mathopt.Model, expr, *, priority: int, is_maximize: bool, name: str = ""):
    """add_auxiliary_objective that leaves the other auxiliary objectives alone.

    In OR-Tools 9.15, add_auxiliary_objective(expr=...) erases the terms of every auxiliary objective
    already in the model; this one creates the objective empty and sets its terms one at a time.
    """
    obj = model.add_auxiliary_objective(priority=priority, is_maximize=is_maximize, name=name)
    flat = mathopt.LinearExpression(expr)
    obj.offset = flat.offset
    for var, coefficient in flat.terms.items():
        obj.set_linear_coefficient(var, coefficient)
    return obj


def objectives_in_order(model: mathopt.Model) -> list:
    """The primary objective and every auxiliary one, lowest priority number first."""
    return sorted([model.objective, *model.auxiliary_objectives()], key=lambda obj: obj.priority)


def allowed_loss(best: float, params: mathopt.ObjectiveParameters | None) -> float:
    """How far an objective may move from its optimum: the larger of the two tolerances, or 0."""
    if params is None:
        return 0.0
    absolute = params.objective_degradation_absolute_tolerance or 0.0
    relative = (params.objective_degradation_relative_tolerance or 0.0) * abs(best)
    return max(absolute, relative)


def solve_in_order(model: mathopt.Model, model_params: mathopt.ModelSolveParameters | None = None):
    """Returns (values by objective name, variable values of the last solve, by variable name)."""
    tolerances = model_params.objective_parameters if model_params else {}
    work = mathopt.Model.from_model_proto(model.export_model())     # a copy; the model stays as it is
    for aux in list(work.auxiliary_objectives()):
        work.delete_auxiliary_objective(aux)
    reached = {}
    for obj in objectives_in_order(model):
        expr = obj.offset + mathopt.fast_sum(t.coefficient * work.get_variable(t.variable.id)
                                             for t in obj.linear_terms())
        work.set_linear_objective(expr, is_maximize=obj.is_maximize)
        with quiet():
            result = mathopt.solve(work, mathopt.SolverType.HIGHS, params=EXACT)
        if result.termination.reason != mathopt.TerminationReason.OPTIMAL:
            raise RuntimeError(f"{obj.name or 'primary'}: {result.termination}")
        best = result.objective_value()
        reached[obj.name or "primary"] = best
        loss = allowed_loss(best, tolerances.get(obj))
        if obj.is_maximize:                                          # keep it within its tolerance
            work.add_linear_constraint(expr >= best - loss, name=f"keep_{obj.name or 'primary'}")
        else:
            work.add_linear_constraint(expr <= best + loss, name=f"keep_{obj.name or 'primary'}")
    values = {v.name: result.variable_values(v) for v in work.variables()}
    return reached, values
