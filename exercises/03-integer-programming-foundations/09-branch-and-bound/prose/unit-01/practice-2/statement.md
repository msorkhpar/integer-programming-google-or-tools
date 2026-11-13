The depot model's search has found a fractional variable at a node and must split the node in two.
A node is described by its bounds: a dict that maps each integer variable's name to a pair
`(lo, hi)`, meaning $`\text{lo} \le x \le \text{hi}`$.

Write `children(bounds, name, value)` in `children.py`. `value` is the LP value of variable `name`
at this node, and it is fractional. Return a pair `(down, up)` of new bounds dicts:

```math
\text{down: } \text{lo} \le x_\text{name} \le \lfloor \text{value} \rfloor, \qquad
\text{up: } \lceil \text{value} \rceil \le x_\text{name} \le \text{hi}
```

where `(lo, hi)` are the node's bounds on `name`. Every other variable keeps its bounds in both
children. The caller keeps the node's own `bounds` to log it, so leave that dict as it was.
