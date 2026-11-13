"""Lesson 7.1.3: one GridCap planning cycle, from Initial to Budget Lock, with a copied scenario and a rerun.

GridCap is a fictional utility's portfolio, generated for this course; no number in it is real. The
four stage names are the ones a CIPT (lesson 7.1.1) uses; what each stage allows here is this course's
reading of them, not any real utility's procedure.
"""

from copy import deepcopy

from gridcap import REGIONS, generate
from cycle_model import Scenario, base_scenario, money, optimize

small = generate("small")
STAGES = ("Initial", "Pre-Opt", "Post-Opt", "Budget Lock")
stage: dict[str, str] = {}


def checks(s: Scenario) -> list[str]:
    """Initial-stage data checks: each must-do fits the budgets alone, each floor can be reached."""
    problems = []
    for p in s.portfolio.projects:
        if p.must_do and not any(all(a <= s.budget[y] for y, a in p.spend(t).items()) for t in p.starts()):
            problems.append(f"{p.project_id} fits no start year")
    for r in REGIONS:
        if s.floor[r] > sum(p.capex for p in s.portfolio.projects if p.region == r):
            problems.append(f"{r} floor above everything the region asks for")
    return problems


def edit(s: Scenario, **changes) -> None:
    """Change a scenario's inputs. A locked scenario refuses; a solved one goes back to Pre-Opt."""
    if stage[s.name] == "Budget Lock":
        raise PermissionError(f"{s.name} is locked; copy it to change it")
    for key, value in changes.items():
        setattr(s, key, value)
    if stage[s.name] == "Post-Opt":
        stage[s.name] = "Pre-Opt"


def copy(s: Scenario, name: str) -> Scenario:
    new = deepcopy(s)
    new.name, new.parent = name, s.name
    stage[name] = "Initial"
    return new


def show(s: Scenario, note: str) -> None:
    print(f"[{stage[s.name]:11}] {s.name:9} {note}")


def diff(a: dict[str, int], b: dict[str, int]) -> str:
    dropped = sorted(set(a) - set(b))
    added = sorted(set(b) - set(a))
    moved = [f"{i} {a[i]}->{b[i]}" for i in sorted(set(a) & set(b)) if a[i] != b[i]]
    return f"dropped {dropped}; added {added}; moved {moved}"


# Initial: the candidate list and limits arrive, and are checked before anyone optimizes.
base = base_scenario(small)
stage[base.name] = "Initial"
show(base, f"snapshot {base.snapshot()[:12]}  checks: {checks(base) or 'no problem found'}")
stage[base.name] = "Pre-Opt"
show(base, f"budgets {list(base.budget.values())}, overrides none")
run = optimize(base)
stage[base.name] = "Post-Opt"
show(base, f"{run.status}  NPV {money(run.npv)}  funded {len(run.starts)} of {len(small.projects)}")

# Finance asks what a smaller 2029 envelope would do: a copy, never an edit of the base.
cut = copy(base, "cut-2029")
show(cut, f"copied from {cut.parent}; snapshot {cut.snapshot()[:12]} (same inputs, same id)")
edit(cut, budget={**cut.budget, 2029: 6_000})
show(cut, f"2029 budget {money(base.budget[2029])} -> {money(cut.budget[2029])}; snapshot {cut.snapshot()[:12]}")
stage[cut.name] = "Pre-Opt"
show(cut, f"checks: {checks(cut) or 'no problem found'}")
cut_run = optimize(cut)
stage[cut.name] = "Post-Opt"
show(cut, f"{cut_run.status}  NPV {money(cut_run.npv)}  funded {len(cut_run.starts)}")
print(f"{'':25}base -> cut-2029: {diff(run.starts, cut_run.starts)}")

# Post-Opt review: a planner forces in the Ridge undergrounding job P024; the base goes back to Pre-Opt.
edit(base, force_in={"P024"})
show(base, f"planner forces in P024; snapshot {base.snapshot()[:12]}")
forced = optimize(base)
stage[base.name] = "Post-Opt"
show(base, f"{forced.status}  NPV {money(forced.npv)}  the override costs {money(run.npv - forced.npv)}")
print(f"{'':25}before -> after override: {diff(run.starts, forced.starts)}")

# Budget Lock: the plan of record is frozen with the snapshot it came from.
stage[base.name] = "Budget Lock"
show(base, f"plan of record: snapshot {forced.snapshot[:12]}, NPV {money(forced.npv)}")
try:
    edit(base, budget={**base.budget, 2027: 9_500})
except PermissionError as refused:
    show(base, f"edit refused: {refused}")
again = optimize(base)
show(base, f"rerun of the locked snapshot: same plan {again.starts == forced.starts}, same NPV {again.npv == forced.npv}")
