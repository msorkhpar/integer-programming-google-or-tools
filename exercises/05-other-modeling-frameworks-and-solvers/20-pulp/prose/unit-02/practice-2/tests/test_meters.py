import warnings

import pulp

from meters import Site, legacy_build, port_build, port_solve

warnings.simplefilter("ignore", DeprecationWarning)

# A water utility's smart-meter rollout, not the lesson's portfolio.
TOWN = [
    Site("A1", "east", 50, 30, 6),
    Site("A2", "east", 35, 25, 5),
    Site("B1", "west", 45, 40, 4),
    Site("B2", "west", 20, 10, 3),
    Site("C1", "north", 15, 20, 2),
]


def legacy_solve(sites, budget, crew_weeks):
    prob, x, k = legacy_build(sites, budget, crew_weeks)
    prob.solve(pulp.PULP_CBC_CMD(msg=False, gapRel=0))
    assert prob.status == pulp.LpStatusOptimal and prob.sol_status == pulp.LpSolutionOptimal
    return (pulp.value(prob.objective), sorted(sid for sid, v in x.items() if v.varValue > 0.5),
            round(k.varValue))


def same_answer(sites, budget, crew_weeks):
    old, new = legacy_solve(sites, budget, crew_weeks), port_solve(sites, budget, crew_weeks)
    return new is not None and abs(new[0] - old[0]) < 1e-6 and new[1:] == old[1:], old, new


def test_the_port_gives_the_legacy_answer_with_crews_to_spare():
    agree, old, new = same_answer(TOWN, budget=80, crew_weeks=40)
    assert old == (85, ["A1", "B2", "C1"], 0)
    assert agree, (old, new)


def test_the_port_has_the_legacy_rows_and_variables_by_name():
    prob, _, _ = legacy_build(TOWN, budget=80, crew_weeks=40)
    model, x, k = port_build(TOWN, budget=80, crew_weeks=40)
    assert sorted(c.name for c in model.linear_constraints()) == sorted(r.name for r in prob.constraints())
    assert sorted(v.name for v in model.variables()) == sorted(v.name for v in prob.variables())


def test_extra_crews_are_whole_crews():
    agree, old, new = same_answer(TOWN, budget=200, crew_weeks=12)
    assert old == (125, ["A1", "A2", "B1", "B2", "C1"], 1)
    assert agree, (old, new)


def test_at_most_three_extra_crews_are_hired():
    rich = [Site(f"S{i}", "east", 200 - i, 10, 10) for i in range(8)]
    agree, old, new = same_answer(rich, budget=1000, crew_weeks=0)
    assert old == (477, ["S0", "S1", "S2"], 3)
    assert agree, (old, new)
