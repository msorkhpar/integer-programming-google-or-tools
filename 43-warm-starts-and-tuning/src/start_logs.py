"""Which starts does each solver take? Four starts on the Ridge region's next cycle, read from each solver's log."""

from ortools.math_opt.python import mathopt

from cycles import next_cycle
from grb_runs import gurobi, quiet_env
from plan_model import build, instance_set, keys
from quiet import muted
from runs import highs, hint_values, scip
from starts import carry_forward, greedy_fill, repair

ridge = instance_set()[0]
approved = highs(ridge, 1).plan
nxt, _ = next_cycle(ridge, approved, seed=7)
carried, _ = carry_forward(approved, nxt)
filled = greedy_fill(nxt, repair(nxt, carried))
starts = {
    "carried, complete": hint_values(keys(nxt), carried),          # breaks budget rows
    "carried, ones only": {(i, t): 1.0 for i, t in carried.items()},
    "repaired, complete": hint_values(keys(nxt), filled),          # breaks nothing
    "repaired, ones only": {(i, t): 1.0 for i, t in filled.items()},
}
WORDS = {mathopt.SolverType.HIGHS: ("MIP start", "ser-supplied"),
         mathopt.SolverType.GSCIP: ("solution candidate storage",)}


def log_lines(kind: mathopt.SolverType, start: dict) -> list[str]:
    pm = build(nxt)
    hint = mathopt.SolutionHint(variable_values={pm.x[k]: v for k, v in start.items()})
    log: list[str] = []
    params = mathopt.SolveParameters(threads=1, random_seed=1) if kind == mathopt.SolverType.GSCIP else None
    with muted():
        mathopt.solve(pm.model, kind, params=params,
                      model_params=mathopt.ModelSolveParameters(solution_hints=[hint]),
                      msg_cb=mathopt.list_message_callback(log))
    return [line.strip() for line in log if any(w in line for w in WORDS[kind])]


env = quiet_env()
for name, start in starts.items():
    print(f"{name}: {int(sum(start.values()))} starts given, {len(start)} of {len(keys(nxt))} variables")
    for kind, label in ((mathopt.SolverType.HIGHS, "HiGHS"), (mathopt.SolverType.GSCIP, "SCIP")):
        print(f"  {label:<7}", log_lines(kind, start) or "nothing about it")
    print(f"  {'Gurobi':<7}", list(gurobi(env, nxt, 1, start).log) or "nothing about it")

carried_start = starts["carried, complete"]
for label, solve in (("HiGHS", highs), ("SCIP", scip)):
    print(f"{label} with the carried start, seed 1: the same run as with no start:",
          solve(nxt, 1, carried_start) == solve(nxt, 1))
