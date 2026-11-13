"""Lesson 14.1.2: the plan with crews and months, set beside the first plan, the stray line HiGHS
prints when nothing keeps it off standard output, and the tiny season's months under two build orders
of the same model."""

import subprocess
import sys

from snapshots import step_dir, use

use(1)
from vegcrew.data import season_from_dict as load_1      # noqa: E402
from vegcrew.generate import scenario as scenario_1      # noqa: E402
from vegcrew.planner import make_plan as plan_1          # noqa: E402

first = plan_1(load_1(scenario_1("small")))

use(2)
from vegcrew.data import WEEKS_PER_MONTH, season_from_dict  # noqa: E402
from vegcrew.generate import scenario                     # noqa: E402
from vegcrew import planner                               # noqa: E402
from ortools.math_opt.python import mathopt               # noqa: E402
from vegcrew.planner import build, make_plan              # noqa: E402
from vegcrew.report import format_plan                    # noqa: E402

season = season_from_dict(scenario("small"))
plan = make_plan(season)
print(format_plan(season, plan))
print(f"first plan (lesson 14.1.1): {len(first.trims)} trims, risk removed ${first.risk_removed:,}k a year")
print("dropped:", " ".join(sorted(set(first.trims) - set(plan.trims))),
      " added:", " ".join(sorted(set(plan.trims) - set(first.trims))))
crew_weeks = sum(season.circuit(cid).weeks for cid in first.trims)
print(f"the first plan needs {crew_weeks} crew-weeks; the season has "
      f"{season.crews * WEEKS_PER_MONTH * season.months} ({season.crews} crews x {season.months} months x "
      f"{WEEKS_PER_MONTH} weeks)")
model, x = build(season)
print(f"model: {model.get_num_variables()} binary variables, {model.get_num_linear_constraints()} rows")

# The same solve without solve_quietly, in a child process, counting what reaches standard output.
loud = ("from ortools.math_opt.python import mathopt\n"
        "from vegcrew.data import season_from_dict\nfrom vegcrew.generate import scenario\n"
        "from vegcrew.planner import EXACT, build\n"
        "model, x = build(season_from_dict(scenario('small')))\n"
        "mathopt.solve(model, mathopt.SolverType.HIGHS, params=EXACT)\n")
out = subprocess.run([sys.executable, "-c", loud], cwd=step_dir(2), capture_output=True, text=True).stdout
stray = out.splitlines()
print(f"without solve_quietly the program printed {len(stray)} lines, nothing asked for:")
print(" ", stray[0] if stray else "(none)")


def build_month_by_month(season):
    """The same variables, rows and objective as planner.build, with the variables made month by month."""
    model = mathopt.Model(name=f"trim_{season.name}")
    months = range(1, season.months + 1)
    x = {(c.cid, m): model.add_binary_variable(name=f"x_{c.cid}_{m}") for m in months for c in season.circuits}

    def trimmed(cid):
        return mathopt.fast_sum(x[cid, m] for m in months)

    for c in season.circuits:
        model.add_linear_constraint(trimmed(c.cid) <= 1, name=f"once_{c.cid}")
    for m in months:
        model.add_linear_constraint(
            mathopt.fast_sum(c.weeks * x[c.cid, m] for c in season.circuits) <= season.crews * WEEKS_PER_MONTH,
            name=f"crews_{m}")
    model.add_linear_constraint(mathopt.fast_sum(c.cost * trimmed(c.cid) for c in season.circuits) <= season.budget,
                                name="budget")
    model.maximize(mathopt.fast_sum(c.risk * trimmed(c.cid) for c in season.circuits))
    return model, x


def months_of(plan):
    return ", ".join(f"{cid} in month {t.month}" for cid, t in sorted(plan.trims.items(), key=lambda kv: kv[1].month))


tiny = season_from_dict(scenario("tiny"))
as_built = make_plan(tiny)
planner.build = build_month_by_month
by_month = make_plan(tiny)
print("tiny season, the same model built two ways:")
print(f"  variables circuit by circuit: risk removed ${as_built.risk_removed}k, {months_of(as_built)}")
print(f"  variables month by month:     risk removed ${by_month.risk_removed}k, {months_of(by_month)}")
