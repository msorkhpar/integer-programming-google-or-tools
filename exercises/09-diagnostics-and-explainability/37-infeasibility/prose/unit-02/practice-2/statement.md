A water utility's pipe program passes every single-job check: no required job, alone, costs more
than the money it could use. Yet the model has no plan. The program's budget rolls over: money not
spent in a year is added to the next year's. Each job is paid in full in the year it is done, and a
required job must be done by the end of its `deadline` year.

So, by the end of any year $`y`$, the program must have paid for every required job whose
deadline is $`y`$ or earlier, and it cannot have paid more than all the budgets up to $`y`$. A year
where the first sum is larger than the second proves there is no plan, whatever else the model
says. That is a check on several jobs at once, which the single-job checks cannot see.

Write `cumulative_check(items, budget)`. `items` maps a job name to `{"cost", "deadline",
"required"}`, and `budget` maps each plan year to its budget ($k). Return a list of
`(year, due, available)` triples, in year order, one for every year where the required work due by
the end of that year costs more than the money available by then. Return `[]` when no year falls
short. About ten lines.
