A water utility (not GridCap) has approved a set of water-main replacements for the next three years
and must now decide **which contractor crew does each job, and in which year**. Each job $`j`$ is
done once, in one year, by one crew:

- Job $`j`$ may be done in any year from `earliest` to `latest`, both included, and in no other year.
- Crews work at different paces: crew $`c`$ needs $`d_{j,c}`$ weeks for job $`j`$ (`job.weeks[crew]`).
- Crew $`c`$ has $`F_{c,t}`$ free weeks in year $`t`$ (`crew.weeks[year]`), and the jobs it does
  that year must fit in them.
- A **large-diameter** main (`job.large`) may only be given to a **certified** crew (`crew.certified`).
- Crew $`c`$ charges $`r_c`$ ($k per week), so job $`j`$ done by crew $`c`$ costs $`r_c\, d_{j,c}`$.
  The utility wants the cheapest schedule.

Write `build(jobs, crews, years)` in `schedule.py`. It returns the model and a dictionary `x` of
binary variables keyed `(job id, crew id, year)`, where `x[j, c, t] = 1` means crew $`c`$ does job
$`j`$ in year $`t`$. You decide which keys exist.

Each agent of this assignment is a crew *in a year*, with its own capacity. Write the formulation
first: the sets (including the set of allowed job, crew and year triples), the parameters, the
variable with its domain, the objective and each labelled row. Then code it.

The tests fix a schedule and ask the solver whether the model allows it; a schedule that needs a key
your `x` does not have counts as refused. So any correct formulation passes, whether a forbidden
triple has no variable or a row holding it at 0. About fifteen lines.
