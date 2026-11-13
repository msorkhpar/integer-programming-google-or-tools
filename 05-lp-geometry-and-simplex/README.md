# 2.2. LP Geometry and Simplex

What an LP solver is doing when it answers: the allowed plans of a linear program form a region with
straight edges, the best plan sits at a corner of that region, and the simplex method finds it by
walking from corner to corner. This module draws a two-variable GridCap LP, solves it with a
60-line tableau simplex, and then breaks it three ways: no plan at all, value without limit, and a
corner where the walk stalls.

## Contents

1. [Solving a 2-variable LP by picture](README_2.2.1.md)
2. [Simplex as walking between vertices (a tiny tableau implementation)](README_2.2.2.md)
3. [Infeasible, unbounded and degenerate LPs](README_2.2.3.md)
