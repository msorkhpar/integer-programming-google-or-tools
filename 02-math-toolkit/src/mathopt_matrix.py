"""Build the tiny model in MathOpt from the CSR rows, then look at what the solver is handed."""

from ortools.math_opt.python import mathopt

from gridcap import generate
from model_matrix import csr

tiny = generate("tiny")
A, b, names = csr(tiny)

model = mathopt.Model(name="tiny-yearly")
x = [model.add_variable(lb=1 if p.must_do else 0, ub=1, is_integer=True, name=f"x_{p.project_id}")
     for p in tiny.projects]                     # a must-do project is a bound, not a row
for i, name in enumerate(names):
    start, end = A.indptr[i], A.indptr[i + 1]
    row = mathopt.LinearExpression(sum(float(a) * x[j] for j, a in zip(A.indices[start:end], A.data[start:end])))
    model.add_linear_constraint(expr=row, ub=float(b[i]), name=name)

if __name__ == "__main__":
    proto = model.export_model()                    # the model in MathOpt's exchange format
    matrix = proto.linear_constraint_matrix          # its constraint matrix, as triplets
    print("export_model() returns a", type(proto).__name__)
    print("CSR nonzeros:", A.nnz, " rows:", A.shape[0], " MathOpt constraints:", len(list(model.linear_constraints())))
    print("MathOpt matrix:", type(matrix).__name__, "with", len(matrix.coefficients), "entries")
    print("row_ids     :", list(matrix.row_ids)[:9])
    print("column_ids  :", list(matrix.column_ids)[:9])
    print("coefficients:", [int(v) for v in matrix.coefficients][:9])
