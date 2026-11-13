# 7.1.1 How a Utility Plans Capital: Programs, Portfolios, Rate Cases

Every model in sections 1 to 6 took GridCap's budgets, projects and mandates as given and asked
which projects to fund. This section asks where those inputs come from, because an engineer who
builds a capital-planning optimizer is asked about them in every review and every interview. Here
is the situation the rest of the module works in. GridCap's fleet teams have sent in 40 candidate
projects for 2027 to 2031 (the small portfolio). Together they ask for $69,810k. The five yearly
budgets add up to $42,230k. Someone has to decide what is funded, and the decision has to hold up
in front of finance and in front of the state regulator who sets GridCap's rates.

GridCap is a fictional utility, generated for this course. Its projects, budgets and floors are
teaching data and describe no real utility. It comes in three portfolios, tiny (8 projects), small
(40) and medium (400), and each numbers its own projects and assets from P001 and A001, so one ID
names different work in different portfolios: tiny's P003 is a Coast tower set replacement, small's
P003 a Valley circuit clearing. This section says which portfolio an ID comes from whenever a lesson
uses more than one. The facts about how real utilities are regulated come from the sources in the
Further reading line, chiefly the Regulatory Assistance Project's guide *Electricity Regulation in
the US* (Lazar, 2016).

The words this lesson defines, in the order it uses them: **capital** and **operating expense**,
**rate case**, **revenue requirement**, **rate base**, **program**, **portfolio**, **envelope**.

## Capital Buys Assets That Last, So Its Cost Is Recovered Over Their Life

A utility spends money in two ways, and the difference shapes everything below.

- **Capital expenditure** (capex) buys or rebuilds something that serves customers for many
  years: a transmission tower, a substation transformer, a mile of underground cable. The asset
  goes on the books at its cost and is **depreciated**: a share of its cost is counted as an
  expense each year of its accounting life. The RAP guide lists the kinds of things that count:
  buildings, power plants, vehicles, poles, wires, transformers, computers and software.
- **Operating expense** (opex, often called O&M for operations and maintenance) is spent and used
  up within the year: labor, fuel, repairs that do not extend an asset's life, taxes.

Why does this matter to an optimizer? Because the two are recovered from customers differently.
In the regulatory formula below, an operating expense is recovered dollar for dollar in the year
it is spent. A capital dollar is recovered over the asset's life, and while it is not yet
recovered the utility earns a return on it. A capital plan is therefore a commitment that shows up
in customers' rates for decades, and that is why the plan is reviewed so closely.

Every GridCap project is a capital project: each has a `cost_profile` of capital spend per year of
work, and the models of section 6 fund it or not. Whether a particular real utility books a
particular kind of work (vegetation clearing, for instance) as capital or as operating expense is
an accounting and regulatory decision this course does not survey; GridCap simply treats all
three of its programs as capital.

## A Rate Case Turns Capital Into Rates Through the Rate Base

The wires business is treated as a **natural monopoly**: one network per area is cheaper than
several, so one company serves the area and is regulated instead of facing competitors. The RAP
guide puts about 75% of the US population with **investor-owned utilities**, private companies
regulated by their state, and the rest with consumer-owned utilities (municipal utilities,
utility districts and cooperatives), which are governed differently. For an investor-owned
utility, a state commission (a public utility commission, or PUC) decides what it may charge. The
commission does this in a **rate case** (also called a general rate case or rate proceeding):
the utility files evidence of its costs and asks for rates that recover them; commission staff and
**intervenors** (other parties, such as consumer advocates and large customers) test that evidence;
and the commission decides. The RAP guide's typical schedule runs about nine months from the
filing to the decision, with discovery, written testimony, rebuttal and hearings in between.

What the commission decides first is the **revenue requirement**: the total revenue the utility
needs in a year to cover its costs and earn a fair return. The guide gives the basic formula as

```math
\text{revenue requirement} = \text{rate base} \times \text{rate of return} + \text{operating expenses}
```

with depreciation and taxes counted among the operating expenses. The pieces:

- The **rate base** is the utility's investment in long-lived assets that serve customers,
  **net of accumulated depreciation**: plant in service at original cost, less the depreciation
  already charged, plus or minus a few adjustments the commission approves (working capital,
  deferred taxes). An asset that is half depreciated earns a return on half its cost.
- The **rate of return** is the percentage the commission allows the utility to earn on its rate
  base, set high enough to attract capital (debt and equity) for a business of its risk.
- To enter the rate base, an investment must generally be **prudent** (chosen and built at a
  reasonable cost with sound management) and **used and useful** (actually in service, and
  something without which costs would be higher or service worse). A commission can review a
  large project after it is built and **disallow** the part it finds imprudent, so the utility
  never earns on it.

The test year is the 12-month period whose costs and sales the case is built on: a recent actual
year, or a forecast year. A forecast test year rests on the utility's budgets for that year, which
is one route by which a capital plan reaches a rate case.

`revenue_requirement.py` follows one capital addition through this formula. The numbers are
invented: $5,310k placed in service, a 30-year book life with straight-line depreciation (the same
amount every year), a 7.5% allowed return, and the rate base taken as the average of each year's
opening and closing net plant (the guide notes that the average is the usual accounting
recommendation). Taxes, working capital and O&M are left out to keep the arithmetic visible.

```python
def schedule(cost: int, life: int, rate: float) -> list[tuple[int, float, float, float, float]]:
    """(year, average rate base, depreciation, return, revenue requirement) for each year of the life."""
    rows = []
    depreciation = cost / life
    net = float(cost)
    for year in range(1, life + 1):
        closing = net - depreciation
        rate_base = (net + closing) / 2
        earned = rate * rate_base
        rows.append((year, rate_base, depreciation, earned, depreciation + earned))
        net = closing
    return rows
```

```text
capital addition $5,310k, book life 30 years, allowed return 7.5%
year  rate base  depreciation  return  revenue requirement
   1      5,222           177     392                  569
   2      5,044           177     378                  555
   3      4,868           177     365                  542
  10      3,628           177     272                  449
  20      1,858           177     139                  316
  30         88           177       7                  184
collected over 30 years: $11,284k  (capital $5,310k, return $5,974k)
the same $5,310k as an operating expense: $5,310k in the test year, no return
```

Read it in three steps.

- **Depreciation returns the capital.** $5,310k over 30 years is $177k a year, every year. Over the
  whole life it adds up to the $5,310k spent, no more.
- **The return falls as the rate base falls.** In year 1 the average net plant is $5,222k
  ($5,310k less half a year's depreciation), and 7.5% of it is $392k. By year 30 almost everything
  is depreciated and the return is $7k.
- **Customers pay for the addition for 30 years**, $11,284k in all, more than twice its cost. The
  same $5,310k spent as an operating expense would be recovered once, in the year it was spent,
  with no return.

The guide also names the incentive this creates. Because profit is tied to the rate base, the
**Averch-Johnson effect** holds that a utility can raise its profit by investing more. That is one
reason regulators review capital plans for prudence, and one reason the plan an optimizer produces
must be explainable: it is part of the case for what customers will pay.

<!-- practice 1 -->

## A Program Is a Line of Work, and the Portfolio Is Everything Competing for the Same Money

Utilities organize capital spending in layers. This course uses three words for them.

- A **project** is one piece of work on one asset: replace this transformer, rebuild this line,
  trim this circuit. It has a cost, a timing window and a value. This is the unit the optimizer
  says yes or no to.
- A **program** is a line of work with its own team, its own kind of asset and often its own
  budget line: transmission, distribution and vegetation management in GridCap. They are the three
  planning teams a **Capital Investment Planning and Prioritization Tool** (CIPT) serves: the kind
  of software this course builds toward, which decides which capital investments to fund, when, and
  why. Lesson 7.1.2 describes each.
- The **portfolio** is the set of all candidate projects, across programs and regions, that
  compete for the same money in the same planning cycle. Choosing a portfolio is choosing which
  projects, from every program, are funded together.

An **envelope** is the amount of money set aside for a program, a region or a year before
projects are chosen: the budget rows of section 6 are yearly envelopes, and GridCap's
`region_floor` is a floor on what each region receives over the plan, which GridCap's data
defines as a rate-case commitment (lesson 6.5.5 wrote it as a row).

`portfolio_by_program.py` shows what GridCap's small portfolio asks for, program by program and
region by region:

```text
program        projects  must-do  requested ($k)  share
transmission         14        1          43,990    63%
distribution         14        1          21,920    31%
vegetation           12        2           3,900     6%
portfolio            40        4          69,810
budgets 2027-2031: 42,230  requested / budgets = 1.65

region   requested ($k)  floor ($k)
Ridge             15,670       3,130
Valley            21,530       4,300
Coast             20,550       4,110
Plains            12,060       2,410
```

The candidate list asks for 1.65 times the money there is. That ratio is normal for a capital
plan, and it is the reason a plan needs an optimizer at all: if every request fit, there would be
nothing to choose. The programs are also very unequal. Transmission is 63% of what is asked with
14 projects; vegetation is 6% with 12. A rule such as "fund the best projects per dollar until the
money runs out" would compare a $130k trim with a $5,840k line rebuild directly. Whether that is
the right comparison is a value question (lessons 7.4.1 to 7.4.4), not a solver question.

The program then solves the planning model of lesson 7.1.3 (the multi-period model of section 6
with the region floors) and splits the funded capex by program:

```text
the optimized plan funds 27 of 40 projects:
  transmission    26,720 of  43,990 requested
  distribution    11,790 of  21,920 requested
  vegetation       3,120 of   3,900 requested
```

$41,630k of the $42,230k is committed, and every program gets part of what it asked for. No
program envelope was imposed here; each program's share is whatever maximizes total NPV under the
yearly budgets and floors. If GridCap's management wanted at least a fixed share for vegetation,
that would be a new row (lesson 6.5.5 wrote program shares as rows), and its cost could be
measured the way lesson 6.5.1 priced a mandate.

<!-- practice 2 -->

## The Capital Plan Is a Selection Under Budgets the Optimizer Did Not Set

Put the pieces together and the shape of the problem is clear, and it is old. Klevorick's 1966
Princeton paper states the classic **capital rationing** problem: a firm has a fixed budget in each
of $`T`$ periods, and must choose, from the investment opportunities over its horizon, the best
subset that keeps within each period's budget. MIT's *Applied Mathematical Programming*, chapter 9,
writes it as a go/no-go integer program, the kind section 3 taught you to solve:

```math
\max \sum_{j} c_j\, x_j \quad \text{subject to} \quad \sum_j a_{ij}\, x_j \le b_i \;\; (i = 1, \dots, m), \qquad x_j \in \{0, 1\}
```

where $`x_j = 1`$ accepts investment $`j`$, $`c_j`$ is its contribution, $`a_{ij}`$ the amount of
resource $`i`$ (cash in period $`i`$, crews) it uses, and $`b_i`$ the amount available. This is
the multi-dimensional knapsack of lesson 6.3.1, and section 6 extended it with start years,
mandates, dependencies and floors. The OR-Tools knapsack page solves the one-row version with a
dedicated knapsack solver; the GridCap models use MathOpt because every rule after the first
needs more rows than a knapsack has.

What the domain adds is a clear line between what the optimizer decides and what it is given:

| Given to the optimizer | Who sets it |
| --- | --- |
| the yearly budgets $`b_i`$ | management and finance, within what the utility expects to recover in rates |
| floors and commitments, such as GridCap's region floors | rate-case commitments and settlements |
| must-do projects | regulators, safety and compliance obligations (lesson 6.5.1) |
| each project's cost, window and value | the fleet teams, finance (NPV, lessons 7.2.1 to 7.2.4) and asset-health models (lessons 7.3.1 to 7.3.4) |

| Decided by the optimizer | Within |
| --- | --- |
| which discretionary projects are funded | every rule above |
| the start year of every funded project | each project's window |
| which option of an alternative group | one per group (lesson 6.5.3) |

The optimizer never sets the budget. When a planner asks "how much should we spend?", the honest
answer from the model is a set of plans, one per budget, and what each one buys; the budget itself
is a business and regulatory decision. Lesson 7.1.3 shows how the planning cycle runs those plans,
and lesson 7.1.4 what each group of people needs from them.

## Summary

- **Capital buys assets that last, so its cost is recovered over their life.** Operating expenses
  are recovered in the year they are spent; capital through depreciation and a return.
- **A rate case turns capital into rates through the rate base.** Revenue requirement = rate base
  × rate of return + operating expenses; the rate base is plant net of accumulated depreciation,
  and an investment enters it only if prudent and used and useful.
- **A program is a line of work, and the portfolio is everything competing for the same money.**
  GridCap's candidates ask for 1.65 times the budgets, which is why the plan is a selection.
- **The capital plan is a selection under budgets the optimizer did not set.** It is the classic
  capital rationing problem, a multi-dimensional knapsack, extended in section 6.

## Reference

| Term | Meaning |
| --- | --- |
| capital expenditure | spend on an asset that serves for years; depreciated over its life |
| operating expense (O&M) | spend used up in the year; recovered dollar for dollar |
| rate case | the proceeding in which a commission sets a utility's revenue requirement and rates |
| revenue requirement | rate base × rate of return + operating expenses (incl. depreciation, taxes) |
| rate base | plant in service at cost − accumulated depreciation ± approved adjustments |
| prudent; used and useful | the two tests an investment must pass to enter the rate base |
| test year | the 12 months of costs and sales a rate case is built on, historical or forecast |
| program | a line of work with its own team and budget line (transmission, distribution, vegetation) |
| portfolio | all candidate projects competing for the same money in one planning cycle |
| envelope | money set aside for a program, region or year before projects are chosen |

| Quantity in `revenue_requirement.py` | Formula |
| --- | --- |
| depreciation | cost / life, each year |
| rate base in year $`k`$ | average of the opening and closing net plant |
| return | rate of return × rate base |
| revenue requirement | depreciation + return (taxes and O&M left out) |

**Further reading:** the OR-Tools [knapsack problem](https://developers.google.com/optimization/pack/knapsack)
page, the one-budget version of the selection; J. Lazar,
[*Electricity Regulation in the US: A Guide*, 2nd ed.](https://www.raponline.org/knowledge-center/electricity-regulation-in-the-us-a-guide-2/)
(Regulatory Assistance Project, 2016), section 1.1 (utilities as natural monopolies), section
3.1 (investor-owned and consumer-owned utilities), chapter 7 (the rate case schedule), chapter 8 (revenue
requirement, test year, rate base, depreciation, construction costs) and section 12.1 (the
Averch-Johnson effect and prudence reviews); A. K. Klevorick,
[Mathematical Programming and Capital Budgeting Under Risk](https://www.princeton.edu/%7Eerp/ERParchives/archivepdfs/R14.pdf)
(Princeton Econometric Research Program, 1966), whose opening pages state pure capital rationing;
MIT 15.053, [Applied Mathematical Programming, chapter 9](https://web.mit.edu/15.053/www/AMP-Chapter-09.pdf),
section 9.1, capital budgeting as a go/no-go integer program.

## Challenges

1. In `revenue_requirement.py`, change the book life to 50 years. Predict whether customers pay
   more or less in total, and why.
2. A commission disallows $1,000k of the $5,310k as imprudent. Which line of the schedule changes,
   and by how much in year 1?
3. Add a row to the planning model that gives vegetation at least 10% of the funded capex. Predict
   whether it costs anything on GridCap small.

## Design Note: Keep the Budget an Input

It is tempting to let the optimizer "find the right budget" by adding a budget variable and a cost
on it. Resist it unless finance asks for exactly that model. The budget is set by people who weigh
things the model does not hold (rate impact, financing, the rate case's timing), and a plan that
silently moved the budget would be a plan no one authorized. Treat the budget as data, run one
scenario per budget the planners want to compare (lesson 7.1.3), and report what each one buys.

## The Full Programs

Each snippet above is part of a complete program, and each program printed the output the lesson
shows. Open one to read it whole, change it, and run it again: Run starts the program on your copy
of the code, so the course's own files never change.

**revenue_requirement.py.** Follows one invented capital addition through depreciation, rate base
and return, year by year (*A Rate Case Turns Capital Into Rates Through the Rate Base*). *Try:*
Raise the allowed return to 9%. Predict year 1's revenue requirement before you run it.

- Program: [revenue_requirement.py](src/revenue_requirement.py)

**portfolio_by_program.py.** Totals GridCap small's requests by program and region, then splits the
optimized plan's capex by program (*A Program Is a Line of Work*). *Try:* Print the requests by
program and year at each project's earliest start. Which year is asked for most?

- Program: [portfolio_by_program.py](src/portfolio_by_program.py)

**cycle_model.py.** The planning model and scenario record this module's programs import: start
variables, must-do and once rows, alternatives, parents, yearly budgets, region floors and planner
overrides. It runs nothing itself.

- Library: [cycle_model.py](src/cycle_model.py)
