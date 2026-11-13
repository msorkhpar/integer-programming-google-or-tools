The road program's conflict finder has named a conflict: some jobs that must be done, the years
each may still be done in, and the yearly resurfacing budgets they overrun. Each job is paid in
full in the year it is done, and money does not carry over between years. Finance asks one
question: what is the **least total increase** of the yearly budgets that would let every job in
the conflict be done?

For one choice of a year for each job, the increase is the sum, over the years, of how far that
year's spending goes over its budget (0 for a year within budget). The answer is the least such
increase over every choice. An IIS names only a few jobs, so trying every choice is fine.

Write `smallest_raise(years, cost, caps)`: `years` maps each job to the years it may be done in,
`cost` maps each job to its cost ($k), and `caps` maps each year of the plan to its budget ($k).
Return `(increase, choice)`, where `choice` maps each job to its year in a cheapest choice. When
several choices tie, return the first one found when jobs are taken in sorted order and each
job's years in the order given. About twelve lines.
