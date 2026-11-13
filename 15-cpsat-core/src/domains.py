"""Lesson 4.4.1: what a CP-SAT variable is: a name and a finite set of integer values."""

from ortools.sat.python import cp_model

model = cp_model.CpModel()
x = model.new_bool_var("x_P001")                          # a Boolean: the integers 0 and 1
k = model.new_int_var(0, 4, "tranches")                   # an integer from 0 to 4
draw = model.new_int_var_from_domain(                      # only these four values
    cp_model.Domain.from_values([0, 500, 1000, 2000]), "draw")
print(repr(x), "|", repr(k), "|", repr(draw))
print("not x:", ~x)

# Ask for the smallest draw that covers a $700k shortfall: 1000, the next value in the domain.
model.add(draw >= 700)
model.minimize(draw)
solver = cp_model.CpSolver()
status = solver.solve(model)
print(solver.status_name(status), "draw =", solver.value(draw))

# A variable whose values could overflow 64-bit arithmetic is refused before any search.
big = cp_model.CpModel()
spend = big.new_int_var(0, 2**62, "spend")
print("validate:", big.validate())
print("status:", cp_model.CpSolver().status_name(cp_model.CpSolver().solve(big)))
