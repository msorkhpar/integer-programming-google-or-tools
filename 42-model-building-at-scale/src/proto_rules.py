"""What Model.from_model_proto does with a proto that breaks the rules of model.proto.

A two-variable model, exported, then edited four ways and loaded again. A valid edit loads; an
invalid one is refused with a ValueError that names the rule.
"""

from __future__ import annotations

from ortools.math_opt import model_pb2
from ortools.math_opt.python import mathopt

model = mathopt.Model(name="rules")
x = model.add_binary_variable(name="x")
y = model.add_binary_variable(name="y")
model.add_linear_constraint(x + 2 * y <= 2, name="r")
model.maximize(x + y)
good = model.export_model()


def load(label: str, edit) -> mathopt.Model | None:
    proto = model_pb2.ModelProto()
    proto.CopyFrom(good)
    edit(proto)
    try:
        loaded = mathopt.Model.from_model_proto(proto)
    except ValueError as error:
        print(f"{label:26} refused, ValueError: {str(error).split(';')[0]}")
        return None
    entries = sorted((e.linear_constraint.name, e.variable.name, e.coefficient)
                     for e in loaded.linear_constraint_matrix_entries())
    print(f"{label:26} loaded; row r holds {entries}")
    return loaded


def explicit_zero(p):
    p.variables.ids.append(2)
    p.variables.lower_bounds.append(0.0)
    p.variables.upper_bounds.append(1.0)
    p.variables.integers.append(True)
    p.variables.names.append("z")
    p.linear_constraint_matrix.row_ids.append(0)
    p.linear_constraint_matrix.column_ids.append(2)
    p.linear_constraint_matrix.coefficients.append(0.0)


def reverse_row(p):
    m = p.linear_constraint_matrix
    m.column_ids[:] = list(reversed(m.column_ids))
    m.coefficients[:] = list(reversed(m.coefficients))


def same_names(p):
    p.variables.names[:] = ["x", "x"]


def ids_down(p):
    p.variables.ids[:] = [1, 0]


load("an explicit 0.0 for z", explicit_zero)
load("row entries out of order", reverse_row)
load("variable ids decreasing", ids_down)
twins = load("two variables named x", same_names)
try:
    mathopt.solve(twins, mathopt.SolverType.HIGHS)
except Exception as error:                  # OR-Tools 9.15 raises an AttributeError (lesson 4.2.4)
    print(f"{'... then solved':26} refused: {str(error.__context__).split(';')[0]}")
