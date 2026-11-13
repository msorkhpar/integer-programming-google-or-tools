A water utility (a fictional one) keeps its planning scenarios in a **book**: a dictionary from a
scenario's name to a record `{"stage", "inputs", "plan", "parent"}`. Its planning cycle has the
four stages Initial, Pre-Opt, Post-Opt and Budget Lock, and the book must refuse any step that
breaks the cycle. Each function returns `True` when it did the step and `False` when it refused,
and a refused step changes nothing.

Write the six functions in `book.py`:

- `create(book, name, inputs)`: a new scenario in Initial, with its own copy of `inputs`, no plan
  and no parent. A name already in the book is refused.
- `checked(book, name)`: the data checks passed, so an Initial scenario moves to Pre-Opt.
- `optimized(book, name, plan)`: a run finished, so a Pre-Opt scenario moves to Post-Opt and keeps
  the plan.
- `edit(book, name, changes)`: update the inputs with `changes`. A scenario in Budget Lock refuses.
  An edit to a scenario in Post-Opt makes its plan out of date: it goes back to Pre-Opt and loses
  its plan. In Initial or Pre-Opt the stage stays as it is.
- `lock(book, name)`: a Post-Opt scenario becomes the plan of record. There is only ever one: while
  any scenario of the book is in Budget Lock, every other lock is refused.
- `copy(book, source, name)`: a new scenario in Initial whose inputs start as the source's, with no
  plan and `parent` set to the source. Editing either one must never change the other.

Any scenario may be copied, whatever its stage; copying a locked plan of record is how a change
after lock starts. `create` and `copy` refuse a new name that is already in the book. Every other
name the functions receive (the scenario to check, run, edit, lock, or copy from) is one the book
has: the tests never pass an unknown one, and the reference simply looks it up, so an unknown name
raises `KeyError`.

Before you code, draw the four stages and mark which function moves a scenario along each arrow,
and which arrows go back. About thirty lines.
