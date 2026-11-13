A pipeline company has one welding rig. It repairs segments one at a time, and some days it is
booked elsewhere: a safety stand-down, a maintenance visit. Each booking is given as its first and
last day, both included, so `(4, 4)` books day 4 only. Days are numbered from 0.

Write `shortest_schedule(jobs, booked, horizon)` in `rig.py`. `jobs` maps a segment to its days of
work, `booked` lists the bookings, and the rig's work must end by day `horizon`. Return each
segment's start day, chosen so that the last repair ends as early as possible.

The model, with $`J`$ the segments, $`d_j`$ their days of work, $`B`$ the bookings with first and
last day $`f_b`$ and $`l_b`$, and $`H`$ the horizon:

```math
\begin{aligned}
& s_j \in \{0, \dots, H - d_j\} && \forall j \in J && \text{(start day)} \\
& C \in \{0, \dots, H\} && && \text{(the day the last repair ends)} \\
& \min \; C \\
& \text{NoOverlap}\big(\{[s_j, s_j + d_j) : j \in J\} \cup \{[f_b, l_b + 1) : b \in B\}\big) && && \text{(one\_at\_a\_time)} \\
& C = \max_{j \in J} (s_j + d_j) && && \text{(makespan)}
\end{aligned}
```

Each $`[s_j, s_j + d_j)`$ is an interval variable; each booking is a fixed interval. Before you
code a booking, work out its size from its first and last day.

The tests check the schedule you return (no overlap, no booked day used) and how early it ends,
so any optimal schedule passes. Every test's horizon leaves room for a schedule, so you need not
handle the case where none exists; the reference does not check the solve status. About fifteen
lines.
