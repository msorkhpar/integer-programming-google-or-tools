"""Variables: bounds, the integer flag, the three ways to create one, and the unbounded default."""

from ortools.math_opt.python import mathopt

model = mathopt.Model(name="variables")
spend = model.add_variable(lb=0, ub=2500, name="spend")                 # 0 <= spend <= 2500, continuous
crews = model.add_variable(lb=0, ub=6, is_integer=True, name="crews")   # crews in {0, 1, ..., 6}
fund = model.add_binary_variable(name="fund")                           # fund in {0, 1}
poles = model.add_integer_variable(lb=0, ub=40, name="poles")           # poles in {0, 1, ..., 40}

for v in model.variables():
    print(f"{v.name:6} id={v.id}  lb={v.lower_bound:g}  ub={v.upper_bound:g}  integer={v.integer}")

# A variable is a handle into the model: its bounds can be read and changed after it is created.
fund.lower_bound = 1                       # now fund = 1: the decision is fixed
print("fund fixed:", fund.lower_bound, "<= fund <=", fund.upper_bound)

# With no bounds given, a variable may take any real value: -inf < free < +inf.
free = mathopt.Model(name="forgot-the-bounds")
level = free.add_variable(name="level")
print("default bounds:", level.lower_bound, level.upper_bound, "integer:", level.integer)
free.maximize(level)
for solver in (mathopt.SolverType.GLOP, mathopt.SolverType.HIGHS):
    print(f"{solver.name}: {mathopt.solve(free, solver).termination.reason.name}")
