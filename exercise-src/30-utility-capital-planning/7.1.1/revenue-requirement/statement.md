A small water utility (a fictional one) asks its commission for rates. Its pipe and plant
additions are placed in service at the start of a year, and the commission in this exercise uses
three conventions:

- **Straight-line depreciation** over a book life of `life` years: an addition of cost $`C`$ is
  depreciated $`C / \text{life}`$ in its first year of service and in each following year until
  its life is over, and never after.
- **End-of-year rate base**: in year $`y`$, each addition counts at its cost less all the
  depreciation charged on it up to and including year $`y`$, and never below zero. An addition
  not yet in service is not in the rate base.
- **Operating expenses** (O&M) are recovered in the year they are spent, dollar for dollar.

Write `revenue_requirement(additions, life, rate, om, years)` in `rates.py`. `additions` maps the
year an addition is placed in service to its cost ($k), `rate` is the allowed rate of return,
`om` maps a year to that year's O&M ($k, a missing year is 0), and the result maps each year of
`years` to its revenue requirement:

```math
\text{RR}_y = \text{O\&M}_y + \text{depreciation}_y + \text{rate} \times \text{rate base}_y
```

Before you code, work one case by hand: $1,000k placed in 2027, a 4-year life and a 10% return.
What are 2027's depreciation, rate base and revenue requirement, and what is 2031's? Then decide
how one addition's age in year $`y`$ tells you whether it depreciates, and how much of it is left
in the rate base.

This exercise's rate base is the **end-of-year** one, not the lesson's. `revenue_requirement.py`
takes the average of each year's opening and closing net plant, the convention the lesson's source
calls usual; this commission uses the closing value alone, which is also a convention a commission
may set, and which keeps each year's arithmetic to one subtraction. The two differ: for the $1,000k
case above, 2027's rate base is $750k at year end and $875k on average, so the requirement is $325k
here and would be $337.5k with the lesson's average. The tests use the end-of-year values.

The tests compare your numbers with values worked out by hand. About fifteen lines.
