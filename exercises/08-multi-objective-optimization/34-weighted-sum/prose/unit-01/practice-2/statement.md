A bus operator is choosing one of several fleet plans, each scored on two measures to maximize:
on-time performance points and emissions points. The operator will pick by a weighted sum with a
share $`s`$ on the first measure and $`1 - s`$ on the second, but the managers cannot agree on
$`s`$. The analyst wants to show, for each plan, the whole range of shares for which it would be
chosen, so that the managers only have to agree on which side of a few numbers they stand.

Write `share_range(scores, k)` in `shares.py`. `scores[j]` is plan $`j`$'s pair of points. Return
the closed interval `(low, high)` of shares $`s \in [0, 1]`$ at which plan `k`'s weighted score is
at least that of every other plan, or `None` if there is no such share.

Write it in notation first: for one rival $`j`$, what inequality in $`s`$ must hold for plan $`k`$
to score at least as much, and when does it bound $`s`$ from below, from above, or not at all? The
answer for all rivals together is what is left of $`[0, 1]`$.

About twelve lines.
