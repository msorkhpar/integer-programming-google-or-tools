"""The result schema refuses results a planner tool must never receive, and documents every field.

GridCap is fictional; the results below are written by hand to break one rule each.
"""

from pydantic import ValidationError

from schemas import PlanResult, ProjectStart, YearSpend

good = dict(job_id="job-7", snapshot="ab12", status="optimal", message="Best plan found and proven: NPV $900k.",
            npv=900.0, bound=900.0, gap=0.0,
            plan=[ProjectStart(project_id="P1", start_year=2028, program="vegetation", region="Valley",
                               capex=400, npv=900)],
            spend_by_year=[YearSpend(year=2028, spend=400, budget=500, headroom=100)])
print("a consistent result      -> accepted:", PlanResult(**good).status)

# Two results the validator lets through: it checks the pairings above, not the arithmetic.
odd = {
    "optimal, gap 0.06": {**good, "bound": 950.0, "gap": 0.06},
    "no plan, a bound": {**good, "status": "time_limit", "npv": None, "bound": 1000.0, "gap": None, "plan": [],
                         "spend_by_year": []},
}
for label, fields in odd.items():
    print(f"{label:<24} -> accepted:", PlanResult(**fields).status)

broken = {
    "optimal, no npv": {**good, "npv": None, "gap": None},
    "infeasible with a plan": {**good, "status": "infeasible"},
    "gap below zero": {**good, "gap": -0.01},
    "gap but no bound": {**good, "bound": None},
    "status 'done'": {**good, "status": "done"},
}
for label, fields in broken.items():
    try:
        PlanResult(**fields)
        print(f"{label:<24} -> accepted")
    except ValidationError as error:
        first = error.errors()[0]
        print(f"{label:<24} -> refused at {list(first['loc']) or 'the model'}: {first['msg']}")

schema = PlanResult.model_json_schema()
print("fields a planner tool reads, from the JSON Schema:")
for name, spec in schema["properties"].items():
    kinds = [s.get("type", s.get("$ref", "?").split("/")[-1]) for s in spec.get("anyOf", [spec])]
    print(f"  {name:<15} {' or '.join(kinds):<14} {spec.get('description', '')}")
