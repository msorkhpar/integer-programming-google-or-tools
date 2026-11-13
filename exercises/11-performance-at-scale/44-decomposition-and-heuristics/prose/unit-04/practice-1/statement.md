GridCap's undergrounding crews pull cable from standard reels of `reel` metres, cut into pieces of a
few standard lengths; the season needs $`d_k`$ pieces of length $`\ell_k`$. A column generation
master chooses how many reels to cut with each pattern, and after each master solve its cover rows'
duals price one piece of each length. The pricing problem asks for the pattern, the pieces cut from
one reel, worth the most at those prices.

Write the pricing problem first: its variables with domains and bounds, its objective, and its row
with a label. Then write `best_reel(prices, pieces, reel)` to solve it without a solver, and return
`(value, pattern)`: the pattern's worth at the prices and the pattern itself, a dict from piece name
to count (counts of zero left out). `pieces[name]` is `(length, demand)`; lengths and `reel` are
whole metres. On small reels the tests compare your value with every pattern tried by brute force.
One test prices a 1,000-metre reel with eight lengths and up to 30 pieces of each: that is $`31^8`$
count combinations, too many to try one by one, so it stops your function after 10 seconds. Trying
every pattern is not the method this practice asks for.

About twelve lines; dynamic programming over metres used is one way.
