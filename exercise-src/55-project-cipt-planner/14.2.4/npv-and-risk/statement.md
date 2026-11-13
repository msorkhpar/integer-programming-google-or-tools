Finance and the asset team both had comments on the step-03 plan:

> Finance: you value every project at its earliest-start NPV, whatever year you start it. A project
> started in 2030 is worth less than the same project started in 2027; we sent you the NPV for
> every start year. Use it.
>
> Asset management: NPV is not why we replace old equipment. Each project lowers the failure risk of
> one asset. We want to see how much risk a plan removes, and a plan that removes the most of it.

You start from the rule-keeping planner of the lesson before. Price every start: its NPV is the
figure finance quotes for that start year, and the risk it removes is the asset's yearly risk,
failure probability times the cost of a failure, over every year after the work ends to the end of
the plan. The failure probability comes from the asset's Weibull curve. The export says which of
the two the plan maximizes, NPV unless it says risk, and the plan and its report carry both.

The export gives each asset's `age` in the plan's first year; the asset is one year older in each
later year. The report changes in three ways, every amount with thousands commas:

- the funded line keeps its form,
  `funded <n> of <all> projects, capex $<capex>k of $<budgets>k, value $<value>k`, but its value
  is now the plan's objective, what the model maximized, in whole $k (the NPV of the actual starts
  when the export asks for NPV);
- a new line follows it: `NPV $<npv>k, risk reduced $<risk>k (maximized: <objective>)`, NPV in
  whole $k and risk with one decimal;
- each funded project's line ends `capex <capex>  npv <npv>  <name>`: the label `npv` replaces
  `value`, and the amount, right-aligned in 6 characters, is the NPV of the year the project
  starts.

`cipt/goals.py` is the next lesson's stub, as the reference has it; no code of this step imports
it, so leave it as it is.

Run executes `main.py`, which plans the demo export and prints the report; `expected/report.txt` is
the report it should print. Submit runs every test in `tests/`, the earlier steps' included, and
compares Run's report with the expected one.
