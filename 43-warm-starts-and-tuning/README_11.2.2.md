# 11.2.2 The Parameters That Matter: Presolve, Cuts, Heuristics, Focus

A GridCap engineer finds a forum thread about slow MIPs and pastes its advice into the planning
service: "turn heuristics up, set the MIP focus to feasibility, presolve aggressive". Every MIP
solver has many parameters. Which of them matter, what does
each of the big four actually trade, and how would anyone know whether the pasted advice helped?
Lessons 3.3.1 to 3.3.3 opened up presolve, cuts and heuristics one at a time and showed
that switching one off changes the work, not the answer. This lesson treats them as knobs, adds the
fourth one, the solver's **focus**, and measures every setting the way lesson 5.4.2 taught, on two
measures at once. GridCap is a fictional utility; its numbers are teaching data.

**Without a Gurobi license.** The Gurobi results below (the table headed "Gurobi, one thread" and
the Gurobi numbers in the prose) come from `settings_gurobi.py`, which needs a Gurobi license
(lesson 5.3.4 explains the kinds of license and how to give the runner yours). Without one, you can
read those numbers but not reproduce them. The rest runs without a license: `settings_highs.py` on HiGHS, `settings_scip.py` and
`focus_scip.py` on SCIP, `cpsat_clock.py` on CP-SAT, `knobs.py`, and all of the lesson's practices.

## The Model

The regional timing model of lesson 11.2.1, unchanged, on the eight regional plans of its first
cycle (`plan_model.instance_set()`: four regions of the medium portfolios drawn with seeds 2027 and
1). No parameter in this lesson changes which plans are allowed or which is optimal: every run below
proves the same optimum for its plan.

**Sets.** $`P`$ the region's projects; $`Y`$ the ten plan years; $`T_i \subseteq Y`$ the start years
of project $`i`$; $`M \subseteq P`$ the must-do projects; $`\mathcal{G}`$ the alternative groups;
$`C \subseteq P`$ the child projects, with parent $`p(c)`$ and lag $`L_c`$.

**Parameters.** $`\text{npv}_{i,t}`$ ($k); $`c_{i,k}`$, the spend of project $`i`$ in its $`k`$-th
year of work ($k); $`B_y`$, the region's budget in year $`y`$ ($k).

**Variables.** $`x_{i,t} \in \{0, 1\}`$ for $`i \in P`$, $`t \in T_i`$.

**Objective and constraints.**

```math
\begin{aligned}
\max \;& \sum_{i \in P} \sum_{t \in T_i} \text{npv}_{i,t}\, x_{i,t} \\
\text{s.t. }& \sum_{t \in T_i} x_{i,t} \le 1 \quad \forall i \in P \setminus M && \text{(once}_i) \\
& \sum_{t \in T_i} x_{i,t} = 1 \quad \forall i \in M && \text{(must}_i) \\
& \sum_{i \in g} \sum_{t \in T_i} x_{i,t} \le 1 \quad \forall g \in \mathcal{G} && \text{(alt}_g) \\
& \sum_{u \in T_c,\, u \le t} x_{c,u} \le \sum_{s \in T_{p(c)},\, s \le t - L_c} x_{p(c),s} \quad \forall c \in C,\ t \in T_c && \text{(after}_{c,t}) \\
& \sum_{i \in P} \sum_{t \in T_i,\, t \le y} c_{i,\,y-t}\, x_{i,t} \le B_y \quad \forall y \in Y && \text{(budget}_y)
\end{aligned}
```

## Four Knobs, and Each Solver Names Them Differently

The four parameters this lesson covers are the ones every MIP solver has in some form, and the
ones the solvers' own guidance points to first:

- **Presolve**: how hard to simplify the model before the search (lesson 3.3.2).
- **Cuts**: how many cutting planes to add to tighten the LP bound (lesson 3.3.1).
- **Heuristics**: how much effort goes to finding plans outside the tree search (lesson 3.3.3).
- **Focus**: which side of the gap to favour. A MIP solver works on two numbers (lesson 3.4.1): the
  incumbent, which only plans can raise, and the bound, which only proof can lower. Focus tilts
  the whole search toward one of them.

MathOpt gives the first three common names: `SolveParameters(presolve=..., cuts=..., heuristics=...)`,
each an `Emphasis` from `OFF` through `LOW`, `MEDIUM`, `HIGH` to `VERY_HIGH`. Its docstring says a
solver's default usually maps to `MEDIUM`, a solver without the feature accepts only an unset value,
and when a setting is given both by its common name and in the solver's own parameters, the
solver's own wins. `knobs.py` tries each knob at `OFF` and `HIGH` on each MathOpt MIP solver:

```text
         presolve   cuts       heuristics   (each tried at OFF and HIGH)
HiGHS    taken      refused    taken
SCIP     taken      taken      taken
CP-SAT   taken      taken      refused
  HiGHS cuts: cuts solve parameter unsupported for HiGHS
  CP-SAT heuristics: Setting the heuristics (was set to EMPHASIS_HIGH) is not supported for CP_SAT solver
```

"Taken" means only that the solve did not fail. For HiGHS the program then checks whether the
common `heuristics` knob does anything, against HiGHS's own option for the same thing,
`mip_heuristic_effort` (default 0.05, the share of effort spent on heuristics, per HiGHS's option
list):

```text
HiGHS on the Valley plan, seed 1: LP iterations to prove optimality
  default                        29,414
  common heuristics=OFF          29,414
  common heuristics=VERY_HIGH    29,414
  mip_heuristic_effort=0.3       29,235
  mip_heuristic_effort=0.8       31,900
```

The common knob is accepted at every level and changes nothing; HiGHS's own option changes the run.
The same was seen for `OFF` on the model of lessons 3.3.1 to 3.3.3; here it holds at `VERY_HIGH` too. So the rule
for every knob: **set it in the solver's own parameters, and check that it changed something.** The
table names the four knobs in each solver's own terms:

| Knob | HiGHS option | SCIP (`GScipParameters`) | Gurobi parameter | CP-SAT |
| --- | --- | --- | --- | --- |
| presolve | `presolve`: `"off"`, `"choose"`, `"on"` | `presolve`: `OFF`, `FAST`, `AGGRESSIVE` | `Presolve`: 0, 1, 2 (-1 automatic) | `cp_model_presolve` |
| cuts | none through MathOpt | `separating`: `OFF`, `FAST`, `AGGRESSIVE` | `Cuts`: 0, 1, 2 (-1 automatic) | MathOpt's common `cuts` (taken above) |
| heuristics | `mip_heuristic_effort`, 0 to 1 | `heuristics`: `OFF`, `FAST`, `AGGRESSIVE` | `Heuristics`: share of time, default 0.05 | refused through MathOpt; its workers (lesson 4.6.1) |
| focus | none | `emphasis`: `FEASIBILITY`, `OPTIMALITY`, ... | `MIPFocus`: 1 plans, 2 proof, 3 bound | none |

SCIP's settings go into `SolveParameters.gscip`. The `gscip.proto` comments say SCIP applies the
emphasis first, then the three meta-settings, then any single parameter, so a single parameter can
always override a meta-setting:

```python
    if gscip is not None:
        params.gscip.CopyFrom(gscip)
```

```python
G = gscip_pb2.GScipParameters
SETTINGS = {
    "default": None,
    "presolve OFF": G(presolve=G.OFF),
    "separating (cuts) OFF": G(separating=G.OFF),
    "heuristics OFF": G(heuristics=G.OFF),
}
```

## Judge a Setting on Two Measures: a Good Plan Soon, and the Proof

A planner looking at a running solve sees two things: the best plan so far, and whether the solver
has finished. A setting can move them in opposite directions, so each setting below is judged on
both, with the measures of lesson 11.2.1:

- **to 1%**: the work until a plan within 1% of the plan's optimum was found;
- **to proof**: the work to prove optimality, with the gap tolerance at 0.

Each is compared with the default over the eight plans and seeds 1, 2 and 3, 24 paired observations,
as a ratio of shifted geometric means (below 1 means less work) with the wins and losses:

```python
        r1, w1, l1 = compare([r.within(best[r.instance], 0.01) for r in mine],
                             [r.within(best[r.instance], 0.01) for r in base], shift)
        rp, wp, lp = compare([r.work for r in mine], [r.work for r in base], shift)
```

```python
def compare(new: list[float], old: list[float], shift: float) -> tuple[float, int, int]:
    """Paired observations of two settings: (SGM of new / SGM of old, new wins, new losses)."""
    if len(new) != len(old):
        raise ValueError("the observations must be paired")
    ratio = shifted_geometric_mean(new, shift) / shifted_geometric_mean(old, shift)
    return ratio, sum(a < b for a, b in zip(new, old)), sum(a > b for a, b in zip(new, old))
```

The work to 1% needs the moment each plan was found, in a unit that repeats. SCIP and Gurobi report
it to a callback, and HiGHS in its log (lesson 11.2.1). CP-SAT needs care, and `cpsat_clock.py`
shows why: it reads two of CP-SAT's counters in a solution callback at every new plan.

```python
    def on_solution_callback(self) -> None:
        self.seen.append((round(self.deterministic_time, 4), self.num_branches, self.num_conflicts,
                          self.objective_value))
```

```text
1 worker: 75 plans; at the end of the solve deterministic time 8.6984, branches 193,322
  first plan: det. time 0.0008, branches     894, NPV 42,829
  last plan:  det. time 0.0008, branches 192,566, NPV 50,538
```

Read inside the callback, CP-SAT's deterministic time stood still from the first plan to the last,
at 0.0008, while the solve as a whole used 8.6984. The branch count did move, from 894 to 192,566.
(With several workers the plans found, and when, change between runs, lesson 4.6.3; one worker
keeps this output repeatable.) Lesson 4.6.3 measured CP-SAT's deterministic time at
the end of a solve, where it is right; to date each plan, use a counter you have seen advance. So the
rule for any solver: **before you trust a work counter to date a plan, print it at two plans and
check that it moved.**

<!-- practice 1 -->

## Heuristics Find the Plans: Switched Off, Good Plans Came 7 to 11 Times Later

```text
SCIP, one thread
setting                solved   to 1%    W/L  to proof    W/L
default                 24/24    1.00  0/0        1.00  0/0
presolve OFF            24/24    1.38  9/15       0.64 16/8
separating (cuts) OFF   24/24    1.24  9/12       1.65  6/18
heuristics OFF          24/24   10.74  0/24       1.34  8/16
(24 paired observations; ratios of shifted geometric means of work in LP iterations, shift 100; W/L: less/more work than the default)
```

```text
Gurobi, one thread
setting                solved   to 1%    W/L  to proof    W/L
default                 24/24    1.00  0/0        1.00  0/0
Presolve=0 (off)        24/24    1.05 16/8        1.17  8/16
Presolve=2 (aggr.)      24/24    1.29  5/19       1.07  8/16
Cuts=0 (off)            24/24    0.72  8/11       1.00 12/12
Cuts=2 (aggr.)          24/24    1.58  3/16       1.73  1/23
Heuristics=0            24/24    6.89  0/24       1.43  7/17
Heuristics=0.5          24/24    1.00  0/0        1.16  1/20
MIPFocus=1 (plans)      24/24    1.17  6/9        1.11  6/18
MIPFocus=2 (proof)      24/24    1.41  5/19       1.66  1/23
MIPFocus=3 (bound)      24/24    3.65  3/21       4.29  0/24
(24 paired observations; ratios of shifted geometric means of work in thousandths of a work unit, shift 10; W/L: less/more work than the default)
```

```text
HiGHS, one thread
setting                solved   to 1%    W/L  to proof    W/L
default                 24/24    1.00  0/0        1.00  0/0
presolve=off            24/24    1.06  8/16       0.97 13/11
heuristic effort 0.3    24/24    1.00  0/0        1.00  5/7
no restarts             24/24    1.04  1/1        0.85 17/7
(24 paired observations; ratios of shifted geometric means of work in LP iterations, shift 100; W/L: less/more work than the default)
```

The clearest result in the three tables: with heuristics off, SCIP needed 10.74 times the work to
reach a plan within 1%, and lost on all 24 observations; Gurobi with `Heuristics=0` needed 6.89 times,
also 0 wins in 24. Without heuristics a plan comes only from a node whose LP happens to be integral
(lesson 3.3.3), and the search reaches such nodes late. The proof got slower too (1.34 and 1.43),
because the tree cannot be pruned against an incumbent it does not have yet.

The reverse does not hold. More heuristic effort bought nothing here: Gurobi's `Heuristics=0.5` found
plans within 1% exactly as soon as the default (0 wins, 0 losses: the same work in every observation)
and made the proof 16% slower; HiGHS's effort of 0.3 changed the work in only 12 of 24 observations
and the ratio not at all. The defaults already find good plans within a few hundred LP iterations on
these models (lesson 11.2.1), so there is nothing left for extra heuristics to win.

## Presolve and Cuts Trade Early Plans Against the Proof, Differently on Each Solver

Presolve shrinks the model before the search (lesson 3.3.2). On SCIP, switching it off made the proof
cheaper, 0.64 with 16 wins in 24, and the first good plan later, 1.38. On Gurobi, off made the proof
17% dearer; on HiGHS it changed little either way (0.97 and 1.06). One knob, three solvers, three
answers: presolve that is slow relative to a small model can cost more than it saves, and each
solver's presolve is different code.

Cuts tighten the LP bound (lesson 3.3.1). Off, SCIP's proof needed 1.65 times the work and lost 18
of 24. Gurobi's `Cuts=0` left the proof unchanged on average (1.00, 12 and 12) and found good plans
sooner (0.72), while aggressive cuts (`Cuts=2`) cost 1.73 times the work and lost 23 of 24: on
models this small, extra cuts are LP rows to carry, not bound to gain. HiGHS takes no cut setting
through MathOpt (the table above); its own options for cut rounds are a matter for its option list,
not for this lesson.

HiGHS's `mip_allow_restart` is not one of the four knobs, but it is a reminder that the big four
are not the only ones: with restarts off, HiGHS proved optimality with 15% less work (17 wins, 7
losses), and found good plans as soon as before. (Lesson 3.3.4 read a restart in a HiGHS log.)

## Focus Says Which Side of the Gap to Work On

Gurobi's `MIPFocus` documents its four values: 0 balances the two sides (the default); 1 favours
finding good feasible plans; 2 favours proving the incumbent optimal, for models where good plans
come easily; 3 favours moving the bound, for models where the bound stalls. SCIP has the same idea as
**emphasis settings**: its documentation describes `FEASIBILITY` as detecting feasibility fast and
`OPTIMALITY` as proving optimality fast, among others such as `HARDLP` and `NUMERICS`.

```text
SCIP, one thread
setting                solved   to 1%    W/L  to proof    W/L
default                 24/24    1.00  0/0        1.00  0/0
emphasis FEASIBILITY    24/24    0.39 20/1        1.51  7/17
emphasis OPTIMALITY     24/24    1.41  4/17       1.14  7/17
(24 paired observations; ratios of shifted geometric means of work in LP iterations, shift 100; W/L: less/more work than the default)
```

SCIP's `FEASIBILITY` emphasis did what it says: a plan within 1% with 0.39 of the work, 20 wins and 1
loss. It paid for that on the proof, 1.51, losing 17 of 24. That is the trade a focus makes, and
here it shows cleanly: **a focus moves work from one side of the gap to the other.** It is the right
setting for a service that stops at a work limit and reports the best plan (lesson 11.2.1's
"insurance" case), and the wrong one for a service that must prove its answer.

The settings that favour proof did not prove faster. SCIP's `OPTIMALITY` was slower on both
measures (1.41 and 1.14), and so were Gurobi's `MIPFocus=2` (1.41, 1.66) and `MIPFocus=3` (3.65,
4.29, losing all 24 on proof). Gurobi's own guidance tells you when each value is meant to help:
`MIPFocus=2` when good plans come easily and the proof is the hard part, `3` when the bound barely
moves. On these models neither is the case: the default reaches a plan within 1% in a few
thousandths of a work unit and proves it soon after. A focus setting is a cure for a symptom; read
the log (lesson 3.3.4) and find the symptom first.

<!-- practice 2 -->

## Defaults Win Here, So Change One Knob at a Time and Keep the Default Unless Both Measures Agree

Seventeen settings were tried in the four tables. Two helped on one measure without hurting the
other by more than noise: Gurobi's `Cuts=0` (0.72 to a good plan, 1.00 on proof) and HiGHS without
restarts (0.85 on proof, 1.04 to a good plan). Two traded one measure for the other: SCIP's
`FEASIBILITY` emphasis and SCIP with presolve off. Two changed next to nothing (HiGHS's heuristic
effort 0.3, and HiGHS with presolve off at 1.06 and 0.97). The other eleven were worse on at least one
measure and better on neither, some by a factor of four. The forum thread's advice (heuristics up,
focus on feasibility, presolve aggressive), tried here one knob at a time on Gurobi, helps nowhere:
none of `Heuristics=0.5`, `MIPFocus=1` and `Presolve=2` beats the default on either measure.

Gurobi's parameter guidelines say the defaults generally work well, and also that MIP models often
benefit from tuning (lesson 11.2.3 takes that up); the CP-SAT Primer advises leaving most
parameters at their defaults and improving the model instead. The way to change one anyway:

1. **Name the measure first.** "Faster" means a good plan sooner, or a proof sooner; a setting can do
   one and undo the other.
2. **Change one knob at a time,** against the default, on a fixed instance set with several seeds.
   Two knobs changed together cannot tell you which one did the work.
3. **Adopt it only if both measures agree,** or if the one it hurts is a measure you do not need.
   A ratio near 1 with wins and losses close to even is no effect.
4. **Write the setting down with the reason and the evidence** (the table), so that the next model
   change can check whether it still holds. Lesson 11.2.3 shows why that check is not optional.

## Summary

- **Four knobs, and each solver names them differently.** Set each in the solver's own parameters:
  MathOpt's common `heuristics` was accepted by HiGHS at every level and changed nothing, and its
  common `cuts` was refused.
- **Judge a setting on two measures.** Work to a plan within 1%, and work to proof, both as paired
  ratios over seeds and instances; date each plan with a counter that you have seen advance (CP-SAT's
  deterministic time stood still inside its callback).
- **Heuristics find the plans.** Off, good plans came 10.74 (SCIP) and 6.89 (Gurobi) times later; more
  effort than the default bought nothing.
- **Presolve and cuts trade early plans against the proof, differently on each solver.** Presolve off
  sped up SCIP's proof (0.64) and slowed Gurobi's (1.17); aggressive cuts cost Gurobi 1.73 times the
  work.
- **Focus says which side of the gap to work on.** SCIP's feasibility emphasis reached good plans
  with 0.39 of the work and needed 1.51 times as much to prove them.
- **Defaults win here.** Change one knob at a time, and adopt it only when both measures agree.

## Reference

| Measure the knob moves | Raise it with | Typical cost |
| --- | --- | --- |
| how soon good plans appear | heuristics up; SCIP `FEASIBILITY` emphasis; Gurobi `MIPFocus=1` | the proof |
| how fast the bound falls | cuts up; Gurobi `MIPFocus=3` | LP work per node |
| how small the model is | presolve up | presolve time, which a small model may not repay |
| how fast the proof closes | Gurobi `MIPFocus=2`; SCIP `OPTIMALITY` emphasis | early plans |

| Solver | Where the knobs go |
| --- | --- |
| HiGHS (MathOpt) | `SolveParameters(highs=HighsOptionsProto(string_options={"presolve": "off"}, double_options={"mip_heuristic_effort": 0.3}))` |
| SCIP (MathOpt) | `params.gscip.CopyFrom(GScipParameters(emphasis=..., presolve=..., separating=..., heuristics=...))` |
| Gurobi | `model.Params.Presolve`, `.Cuts`, `.Heuristics`, `.MIPFocus` |
| CP-SAT | `solver.parameters.cp_model_presolve` and the worker portfolio (lesson 4.6.1) |

**Further reading:** the `Emphasis` and `SolveParameters` docstrings in
[`parameters.py`](https://github.com/google/or-tools/blob/stable/ortools/math_opt/python/parameters.py)
(the common `presolve`, `cuts` and `heuristics` knobs, what an unsupported level does, and that a
solver-specific setting wins over the common one);
[`gscip.proto`](https://github.com/google/or-tools/blob/stable/ortools/math_opt/solvers/gscip/gscip.proto)
(SCIP's emphasis and meta-settings, and the order in which they are applied);
[`sat_parameters.proto`](https://github.com/google/or-tools/blob/stable/ortools/sat/sat_parameters.proto)
(`cp_model_presolve`, `cp_model_probing_level`, `max_deterministic_time`); SCIP,
[`type_paramset.h`](https://www.scipopt.org/doc/html/type__paramset_8h.php) (each emphasis setting
and the `DEFAULT`, `AGGRESSIVE`, `FAST`, `OFF` meta-settings, one line each); Gurobi,
[Parameter Guidelines](https://docs.gurobi.com/projects/optimizer/en/13.0/concepts/parameters/guidelines.html)
(`MIPFocus` 1, 2 and 3 and when each helps, `Heuristics`, `Cuts`, `Presolve`, and `WorkLimit` for
repeatable stopping); HiGHS,
[option definitions](https://ergo-code.github.io/HiGHS/dev/options/definitions/) (`presolve`,
`mip_heuristic_effort`, `mip_allow_restart`, `mip_detect_symmetry`); the
[CP-SAT Primer, parameters chapter](https://d-krupke.github.io/cpsat-primer/parameters.html) (most
parameters are best left at their defaults; reduce presolve only when the log shows it dominating).

## Challenges

1. Add Gurobi `Cuts=1` to `settings_gurobi.py`. Predict where it lands between `Cuts=0` and `Cuts=2`
   on each measure.
2. Combine SCIP's `FEASIBILITY` emphasis with heuristics `OFF`. Before running, decide which of the two
   you expect to win on the work to 1%.
3. Measure SCIP's settings to a 1% gap target (`gap=0.01`) instead of to proof. Which settings change
   rank?
4. A service stops every solve after 50 thousandths of a Gurobi work unit. Which of the settings above
   would you test first, and on which measure?

## Design Note: One Report for Every Setting

`settings_bench.report` takes runs and prints the same columns for every solver and every setting:
solved count, the two ratios, the wins and losses. Nothing about a setting is special-cased. That
uniformity is what makes the four tables comparable at a glance, and it is what lesson 11.2.3's tuner
builds on: a tuner is this report run over many settings, with a rule for picking one.

## The Full Programs

Each snippet above is part of a complete program, and each program printed the output the lesson
shows. Open one to read it whole, change it, and run it again: Run starts the program on your copy of
the code, so the course's own files never change. `settings_gurobi.py` needs a Gurobi license (lesson
5.3.4); the free size-limited one is enough.

**knobs.py.** Tries MathOpt's common knobs on HiGHS, SCIP and CP-SAT, then compares HiGHS's common
heuristics knob with its own option (*Four Knobs*). *Try:* Add `scaling` to the knobs tried and predict
which solvers refuse it.

**cpsat_clock.py.** Reads CP-SAT's deterministic time and branch count at each new plan, with one
worker (*Judge a Setting on Two Measures*). *Try:* Print `num_conflicts` too, and predict
whether it moves.

**settings_scip.py, focus_scip.py, settings_gurobi.py, settings_highs.py.** Each setting against the
solver's default on the eight plans and three seeds (*Heuristics Find the Plans* to *Focus*). *Try:*
In `focus_scip.py`, add `G(emphasis=G.HARD_LP)` and predict whether it helps on either measure.

- Program: [knobs.py](src/knobs.py)
- Program: [cpsat_clock.py](src/cpsat_clock.py)
- Program: [settings_scip.py](src/settings_scip.py)
- Program: [focus_scip.py](src/focus_scip.py)
- Program: [settings_gurobi.py](src/settings_gurobi.py)
- Program: [settings_highs.py](src/settings_highs.py)
- Library: [settings_bench.py](src/settings_bench.py)
- Library: [sgm.py](src/sgm.py)
