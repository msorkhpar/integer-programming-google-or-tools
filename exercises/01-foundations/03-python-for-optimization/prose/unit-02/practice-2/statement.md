Each project row has passed its own checks. What is left are the rules no single row can break: they
are about how rows refer to each other. In the selection model each project $`i`$ has one binary
$`x_i`$, a child $`c`$ has the row $`x_c \le x_{p(c)}`$ (parent), and an alternative group $`g`$ has
the row $`\sum_{i \in g} x_i \le 1`$ (alt).

Write `link_problems(projects)` in `links.py`. `projects` is a list of `Project` records (defined at
the top of the file): `pid`, `parent` (an id, or `None`) and `group` (an alternative group, or
`None`). It returns one string per problem, in any order:

| problem | when |
| --- | --- |
| `"duplicate:<id>"` | `<id>` appears in more than one record (once per id, however many copies) |
| `"self-parent:<id>"` | project `<id>` names itself as its parent |
| `"unknown-parent:<id>"` | project `<id>` names a parent that no record has, anywhere in the list |
| `"blocked-child:<id>"` | child `<id>` is in the same alternative group as its parent |

Why is the last one a problem? If child $`c`$ and its parent $`p`$ share a group, the model has both
$`x_c + x_p \le 1`$ (alt) and $`x_c \le x_p`$ (parent). Funding $`c`$ ($`x_c = 1`$) would need
$`x_p = 1`$ by the parent row, and then the alt row reads $`1 + 1 \le 1`$, which is false. So
$`x_c = 0`$ in every allowed plan: the child can never be funded, and the data is surely wrong.

A project with no group shares a group with nobody. A self-parent is reported only as `self-parent`.

About twelve lines.
