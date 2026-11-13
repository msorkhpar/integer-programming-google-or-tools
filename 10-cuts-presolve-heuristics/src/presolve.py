"""A small presolve for 0-1 models: the reductions lesson 3.3.2 names, applied until none applies.

A `BinaryModel` holds  max sum_j c_j x_j  over  0 <= lo_j <= x_j <= hi_j <= 1, x_j integer, and rows
`sum_j a_j x_j <= rhs` (sense "<=") or `= rhs` (sense "=="). Presolve returns a smaller model and
the values it fixed, so postsolve can put the plan back together.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from ortools.math_opt.python import mathopt


@dataclass
class Row:
    coefs: dict[str, float]
    sense: str          # "<=" or "=="
    rhs: float


@dataclass
class BinaryModel:
    objective: dict[str, float]
    rows: dict[str, Row]
    lo: dict[str, int] = field(default_factory=dict)
    hi: dict[str, int] = field(default_factory=dict)

    def __post_init__(self):
        for j in self.objective:
            self.lo.setdefault(j, 0)
            self.hi.setdefault(j, 1)

    def size(self) -> str:
        nonzeros = sum(len(r.coefs) for r in self.rows.values())
        return f"{len(self.rows)} rows, {len(self.objective)} cols, {nonzeros} nonzeros"


def from_selection(model: mathopt.Model) -> BinaryModel:
    """Read a MathOpt 0-1 model (maximize, rows lb <= a.x <= ub) into a BinaryModel."""
    objective = {v.name: model.objective.get_linear_coefficient(v) for v in model.variables()}
    rows = {}
    for con in model.linear_constraints():
        coefs = {v.name: con.get_coefficient(v) for v in model.row_nonzeros(con)}
        if con.lower_bound == con.upper_bound:
            rows[con.name] = Row(coefs, "==", con.lower_bound)
        else:
            rows[con.name] = Row(coefs, "<=", con.upper_bound)
    return BinaryModel(objective, rows)


def activity(row: Row, lo: dict[str, int], hi: dict[str, int]) -> tuple[float, float]:
    """The least and the most  sum_j a_j x_j  can be, over the variables' bounds."""
    least = sum(a * (lo[j] if a > 0 else hi[j]) for j, a in row.coefs.items())
    most = sum(a * (hi[j] if a > 0 else lo[j]) for j, a in row.coefs.items())
    return least, most


@dataclass
class Presolved:
    model: BinaryModel
    fixed: dict[str, int]
    constant: float
    log: list[str]


def presolve(original: BinaryModel) -> Presolved:
    m = BinaryModel(dict(original.objective),
                    {n: Row(dict(r.coefs), r.sense, r.rhs) for n, r in original.rows.items()},
                    dict(original.lo), dict(original.hi))
    fixed: dict[str, int] = {}
    counts = {"singleton row to bound": 0, "fixed by a row's activity": 0, "dual fixing": 0,
              "redundant row": 0}
    log: list[str] = []

    def fix(j: str, v: int, why: str) -> None:
        m.lo[j] = m.hi[j] = v
        counts[why] += 1

    changed = True
    while changed:
        changed = False
        # 1. A row with one variable is a bound on that variable.
        for name, row in list(m.rows.items()):
            if len(row.coefs) == 1:
                (j, a), = row.coefs.items()
                bound = row.rhs / a
                if row.sense == "==":
                    fix(j, round(bound), "singleton row to bound")
                elif a > 0 and bound < 1:          # x_j <= bound < 1 leaves only x_j = 0
                    fix(j, 0, "singleton row to bound")
                elif a < 0 and bound > 0:          # x_j >= bound > 0 leaves only x_j = 1
                    fix(j, 1, "singleton row to bound")
                else:
                    counts["redundant row"] += 1
                del m.rows[name]
                changed = True
        # 2. Activity bounds: a row that can never bind goes; a variable that cannot take a value is fixed.
        for name, row in list(m.rows.items()):
            least, most = activity(row, m.lo, m.hi)
            if row.sense == "<=" and most <= row.rhs:
                del m.rows[name]
                counts["redundant row"] += 1
                changed = True
                continue
            if least > row.rhs + 1e-9:
                raise ValueError(f"row {name} cannot hold: its least activity {least} exceeds {row.rhs}")
            for j, a in row.coefs.items():
                if m.lo[j] == m.hi[j]:
                    continue
                if a > 0 and least + a > row.rhs + 1e-9:
                    fix(j, 0, "fixed by a row's activity")
                    least, _ = activity(row, m.lo, m.hi)
                    changed = True
                elif a < 0 and least - a > row.rhs + 1e-9:
                    fix(j, 1, "fixed by a row's activity")
                    least, _ = activity(row, m.lo, m.hi)
                    changed = True
        # 3. Dual fixing: raising x_j only adds value and only loosens rows, so set it to 1.
        for j, c in m.objective.items():
            if m.lo[j] == m.hi[j]:
                continue
            column = [row.coefs[j] for row in m.rows.values() if j in row.coefs]
            uses = [row for row in m.rows.values() if j in row.coefs]
            if c >= 0 and all(r.sense == "<=" for r in uses) and all(a <= 0 for a in column):
                fix(j, 1, "dual fixing")
                changed = True
        # 4. Substitute every fixed variable: it is a number now, not a decision.
        for j in [j for j in m.objective if m.lo[j] == m.hi[j]]:
            fixed[j] = m.lo[j]
            for row in m.rows.values():
                if j in row.coefs:
                    row.rhs -= row.coefs.pop(j) * fixed[j]
            del m.objective[j], m.lo[j], m.hi[j]
        for name, row in list(m.rows.items()):
            if not row.coefs:
                if (row.sense == "<=" and row.rhs < -1e-9) or (row.sense == "==" and abs(row.rhs) > 1e-9):
                    raise ValueError(f"row {name} is empty and cannot hold")
                del m.rows[name]
                counts["redundant row"] += 1
        log.append(f"{m.size()}  ({', '.join(f'{k} {v}' for k, v in counts.items() if v)})")
        counts = dict.fromkeys(counts, 0)
    constant = sum(original.objective[j] * v for j, v in fixed.items())
    return Presolved(m, fixed, constant, log)


def to_mathopt(m: BinaryModel, name: str = "presolved") -> tuple[mathopt.Model, dict[str, mathopt.Variable]]:
    model = mathopt.Model(name=name)
    x = {j: model.add_binary_variable(name=j) for j in m.objective}
    model.maximize(sum(c * x[j] for j, c in m.objective.items()))
    for rname, row in m.rows.items():
        expr = sum(a * x[j] for j, a in row.coefs.items())
        model.add_linear_constraint(expr == row.rhs if row.sense == "==" else expr <= row.rhs, name=rname)
    return model, x


def tighten(row: Row, lo: dict[str, int], hi: dict[str, int]) -> list[tuple[str, float, float]]:
    """Coefficient tightening on a <= row over binaries, in place. Returns (variable, old a_j, new a_j).

    If the row cannot bind when x_j = 0 (its most activity without j is d below the rhs), then
    lowering a_j and the rhs by d keeps every 0-1 point's verdict and cuts fractional points off.
    """
    changes = []
    for j, a in sorted(row.coefs.items()):
        if a <= 0 or lo[j] == hi[j]:
            continue
        _, most = activity(row, lo, hi)
        d = row.rhs - (most - a)
        if d > 1e-9:
            row.coefs[j] = a - d
            row.rhs -= d
            changes.append((j, a, a - d))
    return changes
