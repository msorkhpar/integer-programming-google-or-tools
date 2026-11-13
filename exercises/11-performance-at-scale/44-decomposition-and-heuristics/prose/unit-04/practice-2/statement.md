The reel cutting of the previous practice, as a whole season: piece $`k`$ is needed $`d_k`$ times,
and the question is how few reels cover every piece. `best_reel` (your pricing problem) is given.

Write the restricted master first, over the patterns $`\Pi'`$ found so far: variables with
domains, objective, and labelled rows. Write the rule that says no new pattern can improve the LP,
and the lower bound on the LP that holds at every iteration.

Then write `reel_columns(pieces, reel)` to return `(lp_value, bounds, reels)`: the master LP's
optimum when no pattern improves it, the lower bound computed after each master solve (one per
solve, in order), and the reels used when the generated patterns are made integer and solved once
with HiGHS. Start from one single-length pattern per piece, as many pieces as fit (and as needed).
Solve each master LP with GLOP through MathOpt. The tests check your answers against a compact
model of the same question.

About twenty lines.
