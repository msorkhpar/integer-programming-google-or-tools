"""Lesson 6.1.3: a counting row can make the model infeasible; count what can and must be chosen first.

GridCap is a fictional utility's portfolio. Two invented minimums, "at least 2 vegetation projects
in every region" and "at least 2 transmission projects in every region", and one invented cap, "at
most 1 vegetation project per region", are checked before solving and then solved.
"""

from gridcap import REGIONS, generate
from selection_model import EXACT, build, groups_of, ids, solve_highs

small = generate("small")


def most_choosable(members: list[str]) -> int:
    """How many of `members` one plan can fund: each alternative group counts once."""
    groups = {small.project(i).alt_group for i in members if small.project(i).alt_group}
    return sum(1 for i in members if not small.project(i).alt_group) + len(groups)


def precheck(program: str, k: int) -> list[str]:
    problems = []
    for r in REGIONS:
        members = ids(small, program=program, region=r)
        if most_choosable(members) < k:
            n = len(members)
            problems.append(f"{r}: {n} candidate{'s' if n != 1 else ''}, at most {most_choosable(members)} in one plan")
    return problems


def precheck_cap(program: str, k: int) -> list[str]:
    problems = []
    for r in REGIONS:
        must = [i for i in ids(small, program=program, region=r) if small.project(i).must_do]
        if len(must) > k:
            problems.append(f"{r}: {len(must)} must-do projects {must}, cap {k}")
    return problems


for program in ("vegetation", "transmission"):
    sel = build(small)
    for r in REGIONS:
        sel.model.add_linear_constraint(sum(sel.x[i] for i in ids(small, program=program, region=r)) >= 2,
                                        name=f"min_{program}_{r}")
    result = solve_highs(sel.model, EXACT)
    print(f"at least 2 {program} projects per region: {result.termination.reason.name}")
    for problem in precheck(program, 2):
        print("  precheck:", problem)

sel = build(small)
for r in REGIONS:
    sel.model.add_linear_constraint(sum(sel.x[i] for i in ids(small, program="vegetation", region=r)) <= 1,
                                    name=f"max_vegetation_{r}")
print(f"at most 1 vegetation project per region: {solve_highs(sel.model, EXACT).termination.reason.name}")
for problem in precheck_cap("vegetation", 1):
    print("  precheck:", problem)

print("alternative groups:", {g: m for g, m in groups_of(small).items()})
