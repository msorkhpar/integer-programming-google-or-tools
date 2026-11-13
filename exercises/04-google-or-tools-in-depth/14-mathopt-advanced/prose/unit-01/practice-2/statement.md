A model reviewer at a water utility wants a plain listing of every indicator constraint in a
model, to check them against the written rules without reading the code that built them. Write
`audit(model)`, which returns one tuple per indicator constraint, in the order
`model.get_indicator_constraints()` gives them:

```
(name, indicator_name, active_value, lower, upper, coefficients)
```

- `indicator_name`: the name of the indicator variable;
- `active_value`: the value of the indicator at which the row must hold, `1` or `0`;
- `lower`, `upper`: the row's bounds, with `-math.inf` or `math.inf` where a side has none;
- `coefficients`: a dict from each variable name in the row to its coefficient.

So for $`z = 1 \Rightarrow 2a + 3b \le 10`$ named `cap`, the tuple is
`("cap", "z", 1, -math.inf, 10.0, {"a": 2.0, "b": 3.0})`.

Read everything from the constraint objects: the tests build models you have not seen. Nothing
needs solving. About eight lines.
