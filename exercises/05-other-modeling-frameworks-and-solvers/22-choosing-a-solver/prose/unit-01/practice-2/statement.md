A team keeps a table of what each solver it may use does with each model feature, built the way
lesson 5.4.1 built its feature probe. For each solver the table holds two sets of feature names:
`"refuses"`, the features the solver rejects with an error, and `"alters"`, the features it accepts
but silently changes (as CP-SAT does with continuous variables). Before benchmarking a new model, the
team screens the candidates.

Write `screen(features, table)` in `screen.py`. `features` is the set of features the model uses.
Return a dict with one verdict per solver in `table`:

- `"refuses <feature>"` if the solver refuses any feature the model uses, naming the alphabetically
  first such feature;
- otherwise `"alters <feature>"` if it alters any feature the model uses, again the alphabetically
  first;
- otherwise `"ok"`.

A refusal costs a failed run; a quiet change costs a wrong plan. Both rule a solver out, and the
verdict names the kind, so a reader knows which one happened. About eight lines.
