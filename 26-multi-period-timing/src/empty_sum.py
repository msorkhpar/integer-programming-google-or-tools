"""A sum over no variables is the number 0: what MathOpt does with a row built from it, and two ways out."""

from ortools.math_opt.python import mathopt

from gridcap import generate

tiny = generate("tiny")
REGIONS = sorted({p.region for p in tiny.projects})


def new_model():
    model = mathopt.Model(name="one_start_per_region_and_year")
    x = {(p.project_id, t): model.add_variable(lb=0, ub=1, is_integer=True, name=f"x_{p.project_id}_{t}")
         for p in tiny.projects for t in p.starts()}
    return model, x


model, x = new_model()
coast_2029 = sum(x[p.project_id, t] for p in tiny.projects for t in p.starts()
                 if p.region == "Coast" and t == 2029)
print("Coast starts in 2029:", repr(coast_2029), "of type", type(coast_2029).__name__)
print("the row built from it:", repr(coast_2029 <= 1))
try:
    model.add_linear_constraint(coast_2029 <= 1, name="cap_Coast_2029")
except TypeError as error:
    print("add_linear_constraint refuses it:", type(error).__name__)

# Way out 1: skip a row whose set is empty.
model, x = new_model()
written = 0
for g in REGIONS:
    for y in tiny.years:
        terms = [x[p.project_id, t] for p in tiny.projects for t in p.starts() if p.region == g and t == y]
        if terms:
            model.add_linear_constraint(sum(terms) <= 1, name=f"cap_{g}_{y}")
            written += 1
print(f"skip empty sets: {written} rows of {len(REGIONS) * len(tiny.years)}")

# Way out 2: start every sum from an empty LinearExpression, so it is an expression even with no terms.
model, x = new_model()
for g in REGIONS:
    for y in tiny.years:
        starts = sum((x[p.project_id, t] for p in tiny.projects for t in p.starts()
                      if p.region == g and t == y), start=mathopt.LinearExpression())
        model.add_linear_constraint(starts <= 1, name=f"cap_{g}_{y}")
rows = list(model.linear_constraints())
print(f"start from LinearExpression(): {len(rows)} rows of {len(REGIONS) * len(tiny.years)}")
empty = [c.name for c in rows if not list(model.row_nonzeros(c))]
print("rows with no variable:", ", ".join(empty))
result = mathopt.solve(model, mathopt.SolverType.HIGHS)
print("HiGHS:", result.termination.reason.name)

print("wrapped after the sum:", type(mathopt.LinearExpression(coast_2029)).__name__)
floor = mathopt.Model(name="empty_floor")
floor.add_linear_constraint(mathopt.LinearExpression() >= 1, name="floor_Coast_2029")
print("an empty sum >= 1:", mathopt.solve(floor, mathopt.SolverType.HIGHS).termination.reason.name)
