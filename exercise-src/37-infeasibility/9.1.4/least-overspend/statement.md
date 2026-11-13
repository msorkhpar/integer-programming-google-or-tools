A school district's facilities plan funds building projects over a few years. Each project, if
funded, spends a fixed amount ($k) in each year listed in its cost dictionary. Some projects are
required by the state inspector; the rest are optional. Each year has its own budget, and money
does not carry over from one year to the next. This year the required projects do not fit, and
the superintendent wants to know the smallest overspend, year by year, that lets every required
project be funded.

Write the formulation first: one 0/1 variable per project, an elastic budget row per year whose
elastic variable is that year's overspend (continuous, at least 0), a row that funds each required
project, and an objective that makes the total overspend as small as possible. Then write
`least_overspend(projects, budget, required)` to build it with MathOpt, solve it with HiGHS at a
relative gap of 0 (`mathopt.SolveParameters(relative_gap_tolerance=0.0)`, so the overspend is a
proven least, as in the lesson's own solves) and
return `{year: overspend}` for every year of `budget`, each rounded to a whole number of $k.

`projects` maps a project name to `{year: cost}`; `budget` maps each year to its budget; `required`
is a set of project names. The tests compare the overspends, so any correct formulation passes.
About fifteen lines.
