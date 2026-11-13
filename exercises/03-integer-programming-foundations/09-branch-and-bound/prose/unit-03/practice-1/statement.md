A crew-rostering MILP runs a branch-and-bound whose waiting nodes are kept in one plain list, and
the team wants to switch node rules with a parameter instead of three data structures.

Write `next_node(waiting, rule)` in `next_node.py`. Each waiting node is a tuple `(id, depth, bound)`:
`id` counts up as nodes are made (a larger id is a newer node), `depth` is its distance from the
root, and `bound` is its parent's LP value. The problem is a maximization. Return the `id` of the
node to solve next:

| `rule` | Takes |
| --- | --- |
| `"depth"` | the greatest depth; among equal depths, the newest (largest id) |
| `"best"` | the highest bound; among equal bounds, the oldest (smallest id) |
| `"breadth"` | the oldest (smallest id) |

`waiting` is never empty, and its entries can be in any order.
