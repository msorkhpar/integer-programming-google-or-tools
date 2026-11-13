"""Lesson 4.4.2: linear rows switched on and off by literals, with no big-M, on GridCap small.

GridCap is a fictional utility's portfolio, and these rules are invented for the course.
"""

from cpsat_models import funded, one_worker, selection
from gridcap import generate

small = generate("small")
capex = {p.project_id: p.capex for p in small.projects}
valley_rest = [p.project_id for p in small.projects if p.region == "Valley" and p.project_id != "P032"]
vegetation = [p.project_id for p in small.projects if p.program == "vegetation"]
transmission = [p.project_id for p in small.projects if p.program == "transmission"]


def solve(sel):
    solver = one_worker()
    status = solver.solve(sel.model)
    return solver, solver.status_name(status)


# 1. One literal: if P032 is funded, the rest of Valley's capex stays within $4,000k.
sel = selection(small, native=True)
x = sel.x
rest = sum(capex[i] * x[i] for i in valley_rest)
sel.model.add(rest <= 4_000).only_enforce_if(x["P032"])
solver, status = solve(sel)
print(f"P032 caps Valley   {status}  objective {solver.objective_value:,.0f}  P032 funded {solver.boolean_value(x['P032'])}"
      f"  rest of Valley ${solver.value(rest):,}k")
print(f"  a big-M row would need M = {sum(capex[i] for i in valley_rest) - 4_000:,}")

# 2. A conjunction: if P017 and P028 are both funded, at most 4 other transmission projects.
sel = selection(small, native=True)
x = sel.x
others = sum(x[i] for i in transmission if i not in ("P017", "P028"))
sel.model.add(others <= 4).only_enforce_if(x["P017"], x["P028"])
solver, status = solve(sel)
print(f"P017 and P028      {status}  objective {solver.objective_value:,.0f}  both funded "
      f"{solver.boolean_value(x['P017']) and solver.boolean_value(x['P028'])}  other transmission {solver.value(others)}")

# 3. A fee that applies when vegetation capex passes $2,000k: one side is enough.
sel = selection(small, native=True)
x = sel.x
fee = sel.model.new_bool_var("office_fee")
veg = sum(capex[i] * x[i] for i in vegetation)
sel.model.add(veg <= 2_000).only_enforce_if(~fee)
sel.model.maximize(sum(p.value * x[p.project_id] for p in small.projects) - 300 * sel.k - 150 * fee)
solver, status = solve(sel)
print(f"vegetation fee     {status}  objective {solver.objective_value:,.0f}  vegetation ${solver.value(veg):,}k"
      f"  fee {solver.boolean_value(fee)}")

# 4. A rebate earned when vegetation capex passes $2,500k: the wrong side, then the right one.
for side in ("veg <= 2500 if not rebate", "veg >= 2501 if rebate"):
    sel = selection(small, native=True)
    x = sel.x
    rebate = sel.model.new_bool_var("rebate")
    veg = sum(capex[i] * x[i] for i in vegetation)
    if side.endswith("not rebate"):
        sel.model.add(veg <= 2_500).only_enforce_if(~rebate)
    else:
        sel.model.add(veg >= 2_501).only_enforce_if(rebate)
    sel.model.maximize(sum(p.value * x[p.project_id] for p in small.projects) - 300 * sel.k + 100 * rebate)
    solver, status = solve(sel)
    print(f"rebate, {side:26} {status}  objective {solver.objective_value:,.0f}"
          f"  vegetation ${solver.value(veg):,}k  rebate {solver.boolean_value(rebate)}")

# 5. Both sides: the flag equals "vegetation capex passes $2,500k" whichever way the objective pulls it.
for pull in (+100, -100):
    sel = selection(small, native=True)
    x = sel.x
    big = sel.model.new_bool_var("big_vegetation")
    veg = sum(capex[i] * x[i] for i in vegetation)
    sel.model.add(veg >= 2_501).only_enforce_if(big)
    sel.model.add(veg <= 2_500).only_enforce_if(~big)
    sel.model.maximize(sum(p.value * x[p.project_id] for p in small.projects) - 300 * sel.k + pull * big)
    solver, status = solve(sel)
    print(f"flag, both sides, pull {pull:+4}  {status}  vegetation ${solver.value(veg):,}k"
          f"  flag {solver.boolean_value(big)}  truthful {solver.boolean_value(big) == (solver.value(veg) > 2_500)}")
