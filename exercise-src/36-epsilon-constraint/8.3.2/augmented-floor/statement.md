A regional hospital replaces aging medical devices within a capital budget. Each replacement keeps
some beds in service (beds that would otherwise close for lack of working equipment) and earns
patient-safety points from the hospital's audit; each has a cost. The board requires at least
`floor` safety points and wants the most beds. When two choices keep the same number of beds, the
board wants the one with more safety points, never a choice another one beats on safety at no cost
in beds. And the board never gives up a bed for extra safety points above its floor.

Write `augmented_choice(devices, budget, floor, span, rho=1e-3)` in `devices.py`. It returns
`(names, slack)`: the sorted tuple of devices to replace, and how many safety points the choice
scores above the floor. It returns `None` when no affordable choice reaches the floor. `span` is the
range of safety points between the payoff table's two ends; the tests pass it. `rho` is the
weight of the slack reward, $`\rho`$ in lesson 8.3.2's objective: while the slack stays within
`span`, the reward is worth at most `rho` beds.

Write the formulation first (sets, parameters with units, variables with their domains, the objective
and every labeled row), then code it with MathOpt and HiGHS. One solve per call. The tests compare
your answer with every affordable choice listed by hand. About eight lines.
