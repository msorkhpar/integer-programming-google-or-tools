A generator rental firm keeps portable generators in yards and sends them to towns after a storm.
Before the season it asks how many generators its road routes could deliver at most.

Write `most_delivered(stock, needs, routes)` in `generators.py`, using `SimpleMaxFlow`.
`stock` maps each yard to the generators it holds, `needs` maps each town to the most it can take,
and `routes` maps `(from, to)` pairs of place names to the most generators that route carries. A
route may pass through a place that is neither a yard nor a town. Return the largest number that
can arrive at the towns in total.

The problem, with a super source $`s`$ joined to every yard and a super sink $`t`$ joined from every
town:

```math
\begin{aligned}
\max\;& v \\
\text{s.t. }& \text{flow out of } n - \text{flow into } n = \begin{cases} v & n = s \\ -v & n = t \\ 0 & \text{otherwise} \end{cases} && \text{(balance}_n) \\
& 0 \le f_{s,y} \le \text{stock}_y, \quad 0 \le f_{i,j} \le \text{route}_{i,j}, \quad 0 \le f_{w,t} \le \text{need}_w
\end{aligned}
```

The solver writes the rows; you give it the arcs. Number the places first (`SimpleMaxFlow` knows
nodes only as integers), and give the super source and sink numbers after them. About fifteen lines.
