"""A solve with no plan reports an infinite bound. What JSON, and pydantic, make of it.

GridCap is fictional. The large portfolio with a 1-second limit ends with no plan (lesson 12.4.2).
"""

import json
from datetime import timedelta

from ortools.math_opt.python import mathopt
from pydantic import BaseModel, ValidationError

from gridcap import generate
from plan_model import build

pf = generate("large")
result = mathopt.solve(build(pf, dict(pf.budget)).model, mathopt.SolverType.HIGHS,
                       params=mathopt.SolveParameters(time_limit=timedelta(seconds=1)))
bound = result.best_objective_bound()
print("termination:", result.termination.reason.name, "| best_objective_bound():", bound)

print("json.dumps               ->", json.dumps({"bound": bound}))
try:
    json.dumps({"bound": bound}, allow_nan=False)
except ValueError as error:
    print("json.dumps(allow_nan=False) ->", error)


class Loose(BaseModel):
    bound: float


sent = Loose(bound=bound).model_dump_json()
print("pydantic, bound: float   ->", sent)
try:
    Loose.model_validate_json(sent)
except ValidationError as error:
    print("  read back              ->", error.errors()[0]["msg"])


class Honest(BaseModel):
    bound: float | None


sent = Honest(bound=None if bound in (float("inf"), float("-inf")) else bound).model_dump_json()
print("pydantic, float | None   ->", sent, "| read back:", Honest.model_validate_json(sent))
