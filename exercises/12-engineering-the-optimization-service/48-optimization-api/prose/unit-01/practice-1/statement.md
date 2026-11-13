A vegetation team plans which overhead circuits to trim this season. Their scheduling tool will call
an API with a JSON body like this:

```json
{"budget": 900,
 "circuits": [{"circuit_id": "C-14", "miles": 12.5, "cost": 300},
              {"circuit_id": "C-22", "miles": 4.0, "cost": 120}]}
```

The optimizer behind the API trusts its input: a negative budget or a repeated circuit would build a
model that answers a question nobody asked. So the API must refuse such a request with a 422 before
any model is built, and say which field is wrong.

In `trim_api.py`, add the rules to the two pydantic models. The endpoint is written. The rules:

- `budget` is a whole number of $k, zero or more. A zero budget is a real request: trim nothing.
- `circuits` has at least one circuit, and no two circuits share a `circuit_id`.
- A circuit's `circuit_id` is not empty, its `miles` is above zero, and its `cost` is zero or more.
- A field the API does not know, at the top or inside a circuit, is refused, not ignored: a
  misspelled `budjet` must never fall back to a default.

The tests send requests through FastAPI's `TestClient` and check the status codes, so any way of
writing the rules that pydantic enforces passes. About ten lines.
