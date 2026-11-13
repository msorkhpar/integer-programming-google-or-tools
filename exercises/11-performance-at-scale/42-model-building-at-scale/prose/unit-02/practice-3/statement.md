GridCap's finance team rewrote the NPV calculation behind the objective. The new code discounts
each year's benefit in a different order of multiplications, so a few coefficients now differ from
the old builder's in the last binary digit, and it also creates variables in a different order. An
exported-proto comparison calls every such pair of models different. The team wants a check that
calls them the same model and still catches every real change.

Write `same_model(a, b, rel_tol=1e-9)` in `compare_models.py`. It compares two MathOpt models by
name, so the order variables and rows were added in does not matter, and returns `True` when they
state the same model:

- the same variable names, each with the same bounds and the same integer flag;
- the same row names, each with the same bounds and the same set of variables in its terms;
- the same objective sense (maximize or minimize) and the same set of variables in the objective;
- every coefficient, and the objective's offset, equal within a relative tolerance: use
  `math.isclose(x, y, rel_tol=rel_tol, abs_tol=0.0)`.

Names, bounds, integrality and sense are compared exactly: none of them comes from arithmetic that
rounds. A variable that appears in one model's row and not in the other's is a difference, even if
the other model would have given it a coefficient near 0. Read a model with `model.variables()`,
`model.linear_constraints()` and `row.terms()`, and `model.objective` with its `is_maximize`,
`offset` and `linear_terms()` (lesson 4.2.1). Run the file to see why exact comparison fails:
`0.1 * 3 == 0.3` is `False` in floating point. About twenty lines.
