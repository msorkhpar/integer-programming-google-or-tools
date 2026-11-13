# 7.1.4 What Planners, Finance and Regulators Each Need From the Optimizer

GridCap's base plan is solved: 27 of 40 projects, NPV $24,260k, every rule kept. Three groups of
people now read it, and each asks a different first question. A planner asks "what is in, when, and
why is my project out?". A finance analyst asks "what do we spend each year, and does it match what
was authorized?". A regulator asks "were the commitments kept, and would you get the same answer
again?". A CIPT's requirements (lesson 7.1.1) put all three in one sentence: planners, finance
partners and regulators rely on the results, so each solution must be correct, deterministic,
explainable and auditable. This lesson reads one plan from each side, then turns their needs into a
**stakeholder-requirements worksheet**: each requirement tied to the model feature that meets it and
to a check that proves it on a real run.

GridCap is a fictional utility, generated for this course; the requirements below are this
course's examples of what each group asks of a CIPT-style optimizer, not any utility's list. The
plan is the base scenario of lesson 7.1.3, built and solved by `cycle_model.py` (its full model is
in that lesson's *The Model* section). Every project ID in this lesson is the small portfolio's:
P003 below is small's must-do circuit clearing, not tiny's Coast tower set of lesson 7.4.1.

A **stakeholder** is anyone who relies on the result or can stop it. A **requirement** is one
thing a stakeholder needs to be true of every result, stated so that it can be checked.

## Planners Need a Plan They Can Act On and Explain

Planners own the projects. They will have to tell a fleet team why its project is in next year,
deferred to 2031, or out, and they will push back with knowledge the model lacks (lesson 7.1.3's
override). So their view of a plan is project by project. `stakeholder_views.py` prints it:

```text
PLANNERS: what is in, when, and what is out
  funded 27 of 40; 9 start later than they could: ['P008 2029->2031', 'P010 2030->2031', 'P011 2029->2031', 'P012 2030->2031', 'P021 2028->2029', 'P025 2027->2028', 'P029 2030->2031', 'P031 2027->2028', 'P039 2027->2028']
  not funded, best value per dollar first:
    P002 transmission capex   460  NPV   386  NPV per $ 0.84
    P030 transmission capex 5,840  NPV 4,374  NPV per $ 0.75
    P038 distribution capex 1,730  NPV 1,166  NPV per $ 0.67
    P036 transmission capex 5,630  NPV 2,928  NPV per $ 0.52
    ... and 9 more
```

Two things a planner will ask about are in this view, and neither is explained by it.

- **Deferrals.** Nine projects start later than their earliest year, each giving up some NPV,
  because each year's budget is nearly full and moving them frees money for work worth more
  (lesson 6.4.1 read the same nine).
- **Good projects left out.** P002 has the best NPV per dollar of everything unfunded, and is still
  out. The reason is not in the ratio: P002 is the repair option for asset A001, whose replacement
  P001 is funded, and the alternative row allows one of the two (lesson 6.5.3). P030 is out for the
  same kind of reason: its group's other option, P031, is funded.

A ratio cannot explain a selection; only the model's rows can. That is the planner's real
requirement: **for every project, a reason in terms of the rules**: a must-do, a window, an
alternative taken, a budget it did not fit. Section 9 builds those reasons: forcing a project in or
out and pricing it (lesson 9.3.2), diffs between scenarios (lesson 9.3.3), and messages written for
planners (lesson 9.3.4). Planners also need speed: a what-if that takes an hour does not get asked.
Section 11 is about keeping runs fast.

## Finance Needs Spend by Year That Matches What Was Authorized

Finance owns the money. Its first question is about each year, because budgets are authorized year
by year and money not spent in a year is, in GridCap's model, simply not spent (lesson 6.4.4 shows
the carry-over alternative). The same plan, read by finance:

```text
FINANCE: what is spent each year, against what was authorized
  year  budget   spend  headroom
  2027   8,890   8,750       140
  2028   8,120   7,970       150
  2029   8,760   8,630       130
  2030   8,610   8,560        50
  2031   7,850   7,720       130
  total 42,230 authorized, 41,630 spent; plan NPV $24,260k
```

Every year is within its budget, and the plan leaves $600k unspent in all, between $50k and $150k a
year: with whole projects costing $130k or more, the last few dollars of a year can rarely be used.
Finance's requirements follow from the table.

- **Spend by year, never only a total.** A plan within its five-year total can still break a year.
- **Spend that adds up.** The yearly spend must equal the capex of the funded projects, spread by
  each project's cost profile; a report that does not reconcile is not trusted again.
- **Value in money terms finance recognizes.** NPV at the company's discount rate, in stated
  dollars (lessons 7.2.1 to 7.2.4), with the solver's status: an NPV from a run that stopped early (lesson
  3.4.1) is a lower bound on the best plan, not the best plan.
- **The cost of every rule and override,** priced the way lesson 7.1.3 priced forcing P024 in.

## Regulators Need Commitments Kept and a Result Anyone Can Reproduce

The regulator does not choose projects, but decides whether customers pay for them. Lesson 7.1.1
gave the tests: an investment enters the rate base if it is prudent and used and useful, and a
commission may review a project after the fact and disallow what it finds imprudent. The RAP guide
also describes **service quality indices**, measures of the frequency and duration of outages and
of customer service, which some commissions tie to penalties or rewards; lesson 7.4.1 turns
reliability measures into project value. The regulator's view of a plan:

```text
REGULATOR: are the commitments kept, and can the result be reproduced
  must-dos: ['P003 in 2031', 'P010 in 2031', 'P017 in 2030', 'P039 in 2028']
  Ridge  floor  3,130  received  8,990
  Valley floor  4,300  received 12,730
  Coast  floor  4,110  received 13,790
  Plains floor  2,410  received  6,120
  status OPTIMAL, settings {'solver': 'HIGHS', 'relative_gap_tolerance': 0.0}, input snapshot b191e84b9365
```

Every must-do is funded and every region receives more than its floor. The last line carries the
two things an auditor needs to repeat the run: the snapshot of the inputs and the solver settings.
That gives the regulator's requirements.

- **Commitments are rows, and each one is checked on the result.** A mandate written as a weight
  can be dropped silently (lesson 6.5.1); written as a row it either holds or the run is
  infeasible.
- **The result can be reproduced.** Given the snapshot, the settings and the same software, a
  rerun gives the same plan. Lesson 7.1.3 saw one rerun repeat; lessons 10.2.1 to 10.2.4 cover
  what a snapshot alone does not fix (threads, time limits, solver versions) and how a run manifest
  records it. A rerun that returns a different plan with the same NPV is not by itself an error:
  a model can have several optimal plans, and which one the solver returns can depend on exactly
  those things (lesson 4.6.3 measured CP-SAT with eight workers returning different plans from run
  to run).
- **Every decision is traceable.** Who changed which input, when, and what it cost: the audit trail
  of lesson 12.1.2. A plan whose overrides cannot be traced cannot be defended as prudent.

<!-- practice 1 -->

## A Requirements Worksheet Ties Each Need to a Model Feature and a Check

Needs written in prose are forgotten; needs written as checks are run on every result. A
**stakeholder-requirements worksheet** is a table with one row per requirement: who needs it, what
it says, which part of the model or the run meets it, and the check that proves it held. In a
requirements document this is often called a **traceability matrix**, because it traces each
requirement to what implements and tests it. `requirements_worksheet.py` writes GridCap's worksheet
as data, each check a function of the run, and evaluates it:

```python
    ("R4", "finance", "each year's spend is within its budget", "budget_y rows",
     lambda: all(spend[y] <= scenario.budget[y] for y in small.years)),
```

```text
id  who       requirement                                  met by                     check
R1  planner   every must-do project is in the plan         must_i rows                PASS
R2  planner   no project starts outside its window         x[i,t] only for t in T_i   PASS
R3  planner   at most one option per alternative group     alt_g rows                 PASS
R4  finance   each year's spend is within its budget       budget_y rows              PASS
R5  finance   spend by year adds up to the funded capex    spend report               PASS
R6  finance   the NPV reported is proven optimal           status and gap 0           PASS
R7  regulator each region receives its rate-case floor     floor_r rows               PASS
R8  regulator the same inputs give the same plan           snapshot + fixed settings  PASS
R9  regulator every funded child follows its parent        after_c,t rows             PASS
```

Four habits make a worksheet useful rather than decorative.

- **Each requirement is checkable on one result.** "The plan is fair to regions" is not; "each
  region receives its floor" is (R7). Rewrite a vague need until a function can return true or
  false on it.
- **The check reads the result, not the model.** R4 sums the plan's spend from the cost profiles;
  it does not trust the budget row to have been written correctly. A missing or wrong row is
  exactly what such a check catches (lesson 12.3.1 writes one test per constraint the same way).
- **A requirement with no check is a gap, and the worksheet says so.** The planners' "a reason for
  every project" has no row here yet, because section 9 builds it; a worksheet that lists it as
  untested is more honest than one that leaves it out.
- **"Proven optimal" means within tolerances.** R6 passes because the solver reported `OPTIMAL`
  with a relative gap tolerance of 0; even then the solver's own feasibility and integrality
  tolerances apply (lesson 10.1.1).

The worksheet is also the shortest answer to an interview question this role is asked: "how do you
know your optimizer is right?" Show the table, say which rows are checked on every run, and say
which needs are not yet covered.

<!-- practice 2 -->

## Summary

- **Planners need a plan they can act on and explain.** Project by project: in, when, out, and a
  reason in terms of the rules, which a value-per-dollar ratio cannot give.
- **Finance needs spend by year that matches what was authorized.** Within each year's budget,
  reconciled to the funded capex, with NPV and the solver's status.
- **Regulators need commitments kept and a result anyone can reproduce.** Mandates as rows checked
  on the result, a snapshot with the settings, and an audit trail.
- **A requirements worksheet ties each need to a model feature and a check.** One row per
  requirement; a need with no check is listed as a gap.

## Reference

| Stakeholder | First question | Needs from the optimizer | Course lessons |
| --- | --- | --- | --- |
| planners | what is in, when, why not mine? | feasible plan, deferrals, reasons, fast what-ifs, overrides | 6.5.6, 9.3.2, 9.3.3, 12.1.2 |
| finance | what do we spend each year? | spend by year within budgets, reconciled, NPV, prices of rules | 6.4.2, 7.2.4, 9.3.2 |
| regulators | were commitments kept; can you repeat it? | mandates and floors as rows, snapshots, settings, audit trail | 6.5.1, 6.5.5, 10.2.4, 12.1.2 |

| Worksheet column | What it holds |
| --- | --- |
| id, stakeholder | who needs it |
| requirement | one statement that is true or false of a result |
| met by | the row, variable or report that implements it |
| check | a function of the run that returns PASS or FAIL |

**Further reading:** the OR-Tools [MathOpt overview](https://developers.google.com/optimization/math_opt),
whose detailed termination reasons are what R6 reads; the OR-Tools MathOpt sample
[`integer_programming.py`](https://github.com/google/or-tools/blob/stable/ortools/math_opt/samples/python/integer_programming.py),
which refuses to read values unless the termination is optimal or feasible; J. Lazar,
[*Electricity Regulation in the US: A Guide*, 2nd ed.](https://www.raponline.org/knowledge-center/electricity-regulation-in-the-us-a-guide-2/)
(Regulatory Assistance Project, 2016), section 12.2.6 (prudence and used-and-useful reviews) and
chapter 22 (service quality indices).

## Challenges

1. Add a requirement R10 for finance, "no year leaves more than $200k unspent", with its check.
   Predict whether it passes on the base plan.
2. Run the worksheet on the cut-2029 scenario of lesson 7.1.3. Predict which rows, if any, fail.
3. Write the planner requirement "every deferred project is listed with its earliest and its plan
   year" as a check on `stakeholder_views.py`'s output.

## Design Note: Write the Worksheet Before the Model

The worksheet is most useful before any code exists. Sit with a planner, a finance analyst and the
regulatory team, write each need as a row, and agree on the check. The rows then become the
model's constraints and the test suite's first tests (section 12). A model built first and
documented after tends to have rows nobody asked for and needs nobody wrote down.

## The Full Programs

Each snippet above is part of a complete program, and each program printed the output the lesson
shows. Open one to read it whole, change it, and run it again: Run starts the program on your copy
of the code, so the course's own files never change.

**stakeholder_views.py.** Solves GridCap's base scenario and prints the planners', finance's and the
regulator's view of the plan (the first three sections). *Try:* Print every unfunded project, not
only four. Predict how many have a funded alternative.

- Program: [stakeholder_views.py](src/stakeholder_views.py)

**requirements_worksheet.py.** GridCap's stakeholder-requirements worksheet, each requirement
checked on a real run (*A Requirements Worksheet Ties Each Need to a Model Feature and a Check*).
*Try:* Drop the region floors from the scenario before the solve. Predict whether R7 still passes.

- Program: [requirements_worksheet.py](src/requirements_worksheet.py)

**cycle_model.py.** The planning model and scenario record the programs import. It runs nothing
itself.

- Library: [cycle_model.py](src/cycle_model.py)
