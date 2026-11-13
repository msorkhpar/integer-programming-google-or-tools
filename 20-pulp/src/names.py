"""How PuLP names rows and variables, and the three ways two names become one."""

import re
import tempfile
import warnings
from pathlib import Path

import pulp

warnings.simplefilter("ignore", DeprecationWarning)


def attempt(label, action):
    try:
        print(f"{label}: {action()}")
    except Exception as error:                     # show the error PuLP raised, cut to its first line
        message = re.sub(r"/\S*/", ".../", str(error).splitlines()[0])   # the path to CBC, shortened
        print(f"{label}: {type(error).__name__}: {message}")


def add(prob, row, name):
    prob += row, name
    return "accepted"


def lp_rows(prob):
    """The rows as the LP file names them."""
    with tempfile.TemporaryDirectory() as folder:
        path = Path(folder) / "model.lp"
        prob.writeLP(str(path))
        lines = path.read_text().splitlines()
    rows = lines[lines.index("Subject To") + 1: lines.index("Bounds") if "Bounds" in lines else None]
    return [line for line in rows if ":" in line]


prob = pulp.LpProblem("names", pulp.LpMaximize)
y = pulp.LpVariable.dicts("y", ["P001", "P002", "P003"], cat="Binary")
prob += pulp.lpSum(y.values()), "value"

# 1. The same name twice: refused when the second row is added.
prob += y["P001"] + y["P002"] <= 1, "alt_G1"
attempt("same name twice", lambda: add(prob, y["P002"] + y["P003"] <= 1, "alt_G1"))

# 2. Names PuLP rewrites: '-', '+', '[', ']', ' ', '>' and '/' are not allowed in an LP file.
prob += y["P001"] <= 1, "cap Ridge"
print("'cap Ridge' is stored as", [row.name for row in prob.constraints()][-1])
prob += y["P002"] <= 1, "budget-2027"
attempt("'budget-2027' then 'budget_2027'", lambda: add(prob, y["P003"] <= 1, "budget_2027"))

# 3. Rows with no name get one from a counter, so the same row has another name in another run.
for extra_first in (False, True):
    auto = pulp.LpProblem("auto", pulp.LpMaximize)
    z = pulp.LpVariable("z", 0, 10)
    auto += z
    if extra_first:
        auto += z >= 1
    auto += z <= 8
    auto += z <= 9
    print(f"unnamed rows{' with one more in front' if extra_first else ''}: name in constraints() "
          f"{[row.name for row in auto.constraints()]}, in the LP file {lp_rows(auto)}")

# 4. Variable names: two keys that differ only in a rewritten character give one name.
x = pulp.LpVariable.dicts("x", ["P-017", "P_017"], cat="Binary")
print("variable names:", {key: var.name for key, var in x.items()})
twice = pulp.LpProblem("twice", pulp.LpMaximize)
twice += x["P-017"] + 2 * x["P_017"], "value"
twice += x["P-017"] + x["P_017"] <= 1, "one"
attempt("solve with a repeated variable name", lambda: twice.solve(pulp.PULP_CBC_CMD(msg=0)))
attempt("checkDuplicateVars()", lambda: twice.checkDuplicateVars() or "no repeats")
