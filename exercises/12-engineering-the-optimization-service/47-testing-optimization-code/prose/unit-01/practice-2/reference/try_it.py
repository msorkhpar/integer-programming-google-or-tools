"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")

from ortools.math_opt.python import mathopt

from crew_cases import YEARS, cases


def crew_rule_accepts(jobs, crews, plan):
    """A model with only the crew rule: job j started in s uses months[k] crew-months in s + k."""
    model = mathopt.Model()
    x = {(j, s): model.add_binary_variable(name=f"x_{j}_{s}")
         for j, (months, first, last) in jobs.items() for s in range(first, last + 1)}
    for y in YEARS:
        used = mathopt.LinearExpression()
        for j, (months, first, last) in jobs.items():
            for s in range(first, last + 1):
                if 0 <= y - s < len(months):
                    used += months[y - s] * x[j, s]
        model.add_linear_constraint(used <= crews[y])
    if any((j, s) not in x for j, s in plan.items()):
        return False
    for (j, s), var in x.items():
        var.lower_bound = var.upper_bound = 1.0 if plan.get(j) == s else 0.0
    result = mathopt.solve(model, mathopt.SolverType.HIGHS)
    return result.termination.reason == mathopt.TerminationReason.OPTIMAL


print("cases written:", len(cases()))
for jobs, crews, plan, allowed in cases():
    print(f"plan {plan}, crews {crews}: stated {allowed}, crew rule says {crew_rule_accepts(jobs, crews, plan)}")
