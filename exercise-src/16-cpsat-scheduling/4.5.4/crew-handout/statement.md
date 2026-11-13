A landscaping company schedules its jobs against a pool of identical crews with a cumulative
constraint, so the plan says when each job starts and how many crews it needs, but not which crews.
The foremen need names. Days are numbered from 0; a job that starts on day `s` and takes `d` days
occupies days `s` to `s + d - 1`, and its crews are free again on day `s + d`.

Write `name_crews(jobs, crews)` in `handout.py`. `jobs` maps a job to `(start, days, need)` and
`crews` lists the crew names. The plan respects the pool: on no day do the running jobs need more
crews than `len(crews)`. Return a dict mapping each job to the list of crew names it gets, so that
each job gets `need` distinct crews and no crew works on two jobs on the same day.

Use the hand-out rule: go through the jobs in order of start day, and give each job crews that are
free on its start day. With $`f_c`$ the first day crew $`c`$ is free (0 at first):

```math
\begin{aligned}
& \text{for each job } j \text{ in increasing } s_j: \\
& \qquad A_j \subseteq \{c : f_c \le s_j\},\ |A_j| = n_j && \text{(free crews)} \\
& \qquad f_c \leftarrow s_j + d_j \quad \forall c \in A_j && \text{(busy until the end)}
\end{aligned}
```

Taking the free crews in name order makes the result easy to read, but any choice works. The tests
check that the names keep every rule. About ten lines.
