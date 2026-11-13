"""Column generation's first iteration by hand: the starting days, their prices, the pricing answer."""

from ortools.math_opt.python import mathopt

from colgen import DAY, TASKS, price_pattern

master = mathopt.Model(name="crew days, first master")
cover = {t: master.add_linear_constraint(lb=need, name=f"cover_{t}") for t, (_, need) in TASKS.items()}
for t, (minutes, need) in TASKS.items():
    per_day = min(need, DAY // minutes)                    # one single-task day per task
    lam = master.add_variable(lb=0, name=f"days_{t}")
    master.objective.set_linear_coefficient(lam, 1)
    cover[t].set_coefficient(lam, per_day)
    print(f"{t:19} {minutes:3} min x {need:2} tasks   start day: {per_day:2} per day")
lp = mathopt.solve(master, mathopt.SolverType.GLOP)
print(f"master LP: {lp.objective_value():.3f} crew-days")
prices = {t: lp.dual_values(cover[t]) for t in TASKS}
print("prices (crew-days per task): " + ", ".join(f"{t} {p:.3f}" for t, p in prices.items()))
worth, pattern = price_pattern(prices)
print(f"pricing: best day {pattern} worth {worth:.3f} days of work, reduced cost {1 - worth:+.3f}")
