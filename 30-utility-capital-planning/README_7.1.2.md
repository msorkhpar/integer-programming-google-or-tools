# 7.1.2 Transmission, Distribution and Vegetation Investments

GridCap's 40 candidate projects come from three teams, and a planner reading the list can tell
them apart at a glance. The transmission team asks for $43,990k with 14 projects, among them a
$5,840k line rebuild. The vegetation team asks for $3,900k with 12, the smallest a $130k circuit
clearing. The distribution team sits between them. These are the three fleets a CIPT (lesson
7.1.1) is built to serve: Transmission, Distribution and Vegetation planning. This lesson explains what
each fleet is, why its projects look the way they do, and which rules of the section 6 model each
one brings with it.

GridCap is a fictional utility, generated for this course: its projects, crews and the circuits
of the vegetation example are teaching data. The facts about real power systems come from the
sources in the Further reading line: the US Energy Information Administration (EIA), the
Regulatory Assistance Project's guide (RAP), and NERC's transmission vegetation standard.

A few words first. A **fleet** is all the assets of one kind a utility owns and maintains, and the
team that plans work on them; in GridCap each fleet is one **program** (lesson 7.1.1). **Voltage**
is measured in volts; a **kilovolt** (kV) is 1,000 volts. A **substation** is a fenced site where
**transformers** change voltage from one level to another. A **circuit** or **feeder** is one
line, with its branches, that carries power out of a substation to customers. A
**right-of-way** is the strip of land a line runs along, which the utility has the right to use
and must keep clear.

## Transmission Moves Bulk Power, So Its Projects Are Few, Large and Long

Power travels from power plants to customers in two stages. EIA describes them as two kinds of
lines joined by transformers at substations: **transmission** lines carry power at high voltage
over long distances, because high voltage makes long-distance transmission more efficient and
cheaper; **distribution** lines carry it at lower voltage, safe for homes and businesses, the last
miles to customers. The RAP guide puts the transmission threshold at about 115 kV and above,
mostly on steel towers, with the highest lines at 345, 500 or 765 kV.

Three things follow for planning.

- **Failures are wide.** A transmission line serves a whole region, not a street. The RAP guide
  describes reliability standards, written by NERC (the North American reliability organization)
  and enforced by FERC (the Federal Energy Regulatory Commission), that hold transmission owners
  responsible for withstanding the loss of a critical element, planning often summed up as
  "N-1". A failure that is not contained can cascade across the system.
- **Projects are large and slow.** Towers, line rebuilds and breaker replacements cost millions
  and take more than one year to build. FERC sets the rates for most bulk power transmission
  (RAP section 3.8), so transmission projects may be reviewed by a different regulator from the
  rest of the portfolio.
- **Work is chained.** A line cannot be rebuilt before the towers that carry it, and an outage on
  a line must be scheduled; transmission is where most parent-child links and repair-or-replace
  choices come from.

`fleets.py` shows what this looks like in GridCap small:

```text
program        projects  capex min / median / max ($k)  years of work  interventions
transmission         14     460 /  2,595 /  5,840          1.6         rebuild, repair, replace
distribution         14     520 /  1,605 /  2,440          1.6         repair, replace, underground
vegetation           12     130 /    320 /    580          1.0         clear, trim, widen
```

The median transmission project costs $2,595k, and the largest $5,840k: more than half of a
year's whole budget (the 2031 budget is $7,850k). One such project funded in a year crowds out
many smaller ones, so the yearly budget rows are where transmission work and everything else
compete.

## Distribution Reaches Every Customer, So Its Projects Are Many and Mid-Sized

Distribution is the system that reaches every customer: substation transformers that step the
voltage down, feeders running out along streets, poles, smaller transformers, and
service lines. EIA notes that the US has thousands of miles of high-voltage lines and millions of
miles of low-voltage ones, so distribution is where the assets are numerous. Local utilities
operate it, and the state commission regulates it (RAP section 13.1 puts lines at 34.5 kV or less
almost always under state regulation).

For the planner this means many mid-sized projects, each affecting fewer customers than a
transmission project, and a value that is measured customer by customer: how often and how long
customers on a feeder are without power. Those reliability measures, and how they become a value
per project, are the subject of lesson 7.4.1. GridCap's distribution projects run from $520k to
$2,440k, and include a kind of work the other fleets lack: putting a line **underground**, which
removes it from storms and trees at a much higher cost than repairing it.

The RAP guide also describes how distribution planning is changing: rooftop solar, batteries and
electric vehicles (distributed energy resources) make power flow both ways on feeders, and some
states now require **integrated distribution planning**, which weighs those resources against
building more wires. That is a source of new candidate projects and new alternatives, not a change
to the selection model itself.

## Vegetation Work Comes Back on a Cycle, So Deferring It Moves Work, Not Removes It

Trees grow into lines. A branch that touches a high-voltage conductor, or comes close enough for
current to arc to it (a **flash-over**), trips the line, and on a transmission line that outage
can spread. NERC's standard FAC-003 exists for this: its stated purpose is to manage vegetation on
transmission rights-of-way to prevent the vegetation-related outages that could lead to cascading.
It applies to overhead transmission lines of 200 kV and above, and to some lower-voltage lines that
planners identify as critical. It requires, among other things, documented maintenance strategies,
**vegetation inspections every year**, and completion of each year's planned work.
FAC-003 says outright that it is not written for tree contact with distribution lines; tree work on
distribution circuits falls under the state's rules, which this course does not survey.

Vegetation projects differ from the other fleets in kind, not only in size. GridCap's are small
($130k to $580k), one year long, and they never end: a trimmed circuit grows back. That makes a
vegetation program a **cycle**: each circuit is trimmed every few years, and the work due in a
year is set by when each circuit was last trimmed. `vegetation_cycle.py` shows it with eight
invented circuits on an invented four-year cycle:

```python
def due_miles(last_trim: dict[str, int]) -> dict[int, int]:
    """Miles due in each year if every circuit is trimmed exactly when its cycle comes round."""
    due = {y: 0 for y in YEARS}
    for c, (miles, last) in CIRCUITS.items():
        year = last_trim[c] + CYCLE
        while year in due:
            due[year] += miles
            year += CYCLE
    return due
```

```text
cycle 4 years; miles due each year when every trim is on time:
  2027:  77  2028:  79  2029:  74  2030:  64  2031:  77  2032:  79  2033:  74  2034:  64
2028 work deferred one year; miles due each year:
  2027:  77  2028:   0  2029: 153  2030:  64  2031:  77  2032:   0  2033: 153  2034:  64
```

On time, the work is level: 64 to 79 miles every year. Defer 2028's two circuits (C03 and C04, 79
miles) by one year and nothing is saved: 2029 now carries 153 miles, twice a normal year, and
because each circuit's cycle restarts from its new trim year, the lump comes back in 2033. The
deferred circuits also went five years between trims instead of four, so they spent a year with
more growth near the lines. Deferring vegetation work moves cost and risk into later years; it
does not remove them. A model that values a trim only by what it costs today will defer it every
year, which is why lessons 7.3.4 and 7.4.4 give each intervention a value that depends on when it
is done.

<!-- practice 1 -->

## Each Fleet Brings Its Own Rows to the Model

The three fleets share one model (lesson 7.1.3 states it in full), but they do not use its rules
equally. `fleet_rules.py` counts, for each GridCap program, the projects that bring each kind of
rule:

```python
for p in small.projects:
    tally = rules[p.program]
    tally["must-do"] += p.must_do
    tally["alternative"] += p.alt_group is not None
    tally["has parent"] += p.parent is not None
    tally["is parent"] += any(c.parent == p.project_id for c in small.projects)
    tally["multi-year spend"] += p.duration > 1
    tally["several start years"] += p.latest_start > p.earliest_start
```

```text
program                     must-do          alternative           has parent            is parent     multi-year spend  several start years
transmission                      1                    4                    1                    1                    8                   11
distribution                      1                    0                    1                    0                    6                    7
vegetation                        2                    0                    0                    1                    0                    9
```

Each column is a rule you have already written:

| Column | Rule it brings | Lesson |
| --- | --- | --- |
| must-do | an equality row, $`\text{started}(i) = 1`$ | 6.5.1 |
| alternative | one at-most-one row per group of options for the same asset | 6.5.3 |
| has parent, is parent | precedence rows with a lag, on both projects | 6.4.3, 6.5.4 |
| multi-year spend | the project's cost spread over the budget rows of several years | 6.4.2 |
| several start years | one start variable per allowed year | 6.4.1 |

The table reads like the fleets. All four alternative projects are transmission: the repair-or-
replace choices for an aging asset (lesson 6.5.3's groups G001 and G030). Vegetation has no
multi-year work, but two of the four must-do projects, which fits vegetation work owed to a
compliance commitment. And a vegetation project is a parent: in GridCap small, the Coast
transmission project P016 may start only after the vegetation project P015 (lesson 6.5.4), the
"clear the corridor before you build" link.

The crews add one more difference. `fleets.py` also prints the crew-months each program asks for
against what GridCap's crews can supply:

```text
program        crew-months asked  crew-months available 2027-2031
transmission                 108  [26, 19, 20, 34, 14]
distribution                  49  [9, 15, 11, 8, 4]
vegetation                    25  [2, 3, 4, 7, 2]
```

Crews are not shared between fleets: a tree crew does not rebuild towers. So a crew limit is a row
per program and per year: the crew-months of that program's projects at work in year $`y`$ are at
most $`K_{g,y}`$, the crew-months program $`g`$ has that year (GridCap's `crews` data). It binds a
fleet on its own even when the money is there. Vegetation asks for 25
crew-months against 18 available over the five years, so on crews alone not every vegetation
project could be done.

<!-- practice 2 -->

## Summary

- **Transmission moves bulk power, so its projects are few, large and long.** High voltage, long
  distances, NERC reliability standards, and most of the chained and either-or work.
- **Distribution reaches every customer, so its projects are many and mid-sized.** Regulated by
  the state, valued by the customers each feeder serves.
- **Vegetation work comes back on a cycle, so deferring it moves work, not removes it.** FAC-003
  requires yearly inspection and planned work on critical transmission lines.
- **Each fleet brings its own rows to the model.** Alternatives and precedence come mostly from
  transmission, compliance must-dos often from vegetation, and crew rows are per fleet.

## Reference

| Fleet | What it is | GridCap small | Typical rules |
| --- | --- | --- | --- |
| transmission | high-voltage lines (about 115 kV and up), towers, breakers, bulk substations | 14 projects, median $2,595k | alternatives, precedence, multi-year spend |
| distribution | lower-voltage feeders, poles, transformers, service to customers | 14 projects, median $1,605k | multi-year spend, undergrounding options |
| vegetation | keeping trees clear of lines on a cycle | 12 projects, median $320k | must-do (compliance), parent of construction |

| Term | Meaning |
| --- | --- |
| substation | a site where transformers change the voltage |
| circuit, feeder | one line out of a substation to customers |
| right-of-way | the land strip a line runs along |
| flash-over | current arcing from a line to something too close to it |
| N-1 | planning so that the loss of any one critical element does not cut service |
| FAC-003 | NERC's transmission vegetation management standard |

**Further reading:** EIA, [Delivery to consumers](https://www.eia.gov/energyexplained/electricity/delivery-to-consumers.php)
(transmission and distribution, and the transformers between them); J. Lazar,
[*Electricity Regulation in the US: A Guide*, 2nd ed.](https://www.raponline.org/knowledge-center/electricity-regulation-in-the-us-a-guide-2/)
(Regulatory Assistance Project, 2016), sections 3.8 and 3.9 (transmission, NERC standards,
right-of-way vegetation), 13.1 (transmission voltages, N-1, the transmission-distribution line)
and chapter 16 (integrated distribution planning); NERC,
[FAC-003-5 Transmission Vegetation Management](https://www.nerc.com/pa/Stand/Reliability%20Standards/FAC-003-5.pdf),
sections A.3 to A.6 (purpose, applicable lines, and the yearly inspection and work requirements).

## Challenges

1. In `vegetation_cycle.py`, defer 2028's work by two years instead of one. Predict the largest
   year and when it comes back.
2. In `fleets.py`, print each program's capex share of each year's budget if every project started
   at its earliest year. Which fleet would a 2031 budget cut hit hardest?
3. Write the crew row for vegetation in 2030 on GridCap small, with $`K = 7`$ crew-months, and add
   it to `cycle_model.build`. Predict whether it changes the plan.

## Design Note: One Model, Fleet Data

It is tempting to build one model per fleet and add the results. Don't: the fleets compete for the
same yearly budget and some of their projects depend on each other (P016 waits for P015). Keep one
model, and keep what differs between fleets in the data: the program on each project, the crews by
program and year, the alternatives and parents. Then a new fleet rule, such as a crew limit, is a
loop over programs, and the solver still trades a transmission rebuild against ten trims.

## The Full Programs

Each snippet above is part of a complete program, and each program printed the output the lesson
shows. Open one to read it whole, change it, and run it again: Run starts the program on your copy
of the code, so the course's own files never change.

**fleets.py.** Compares GridCap small's three programs: project costs, years of work,
interventions and crew-months (*Transmission Moves Bulk Power* and *Each Fleet Brings Its Own
Rows*). *Try:* Add a column with each program's number of distinct regions. Predict whether any
program is missing from a region.

- Program: [fleets.py](src/fleets.py)

**vegetation_cycle.py.** Shows the miles due each year on an invented four-year trim cycle, on time
and with one year's work deferred (*Vegetation Work Comes Back on a Cycle*). *Try:* Change the cycle
to three years. Predict which years carry the most miles.

- Program: [vegetation_cycle.py](src/vegetation_cycle.py)

**fleet_rules.py.** Counts, for each program, the projects that bring each kind of model rule
(*Each Fleet Brings Its Own Rows to the Model*). *Try:* Add a column for projects that can start in
the plan's first year. Predict which fleet has the most.

- Program: [fleet_rules.py](src/fleet_rules.py)
