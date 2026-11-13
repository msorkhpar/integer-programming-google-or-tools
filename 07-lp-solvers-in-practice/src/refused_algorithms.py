"""Which LP algorithm each solver accepts through MathOpt, and what a refusal looks like."""

from ortools.math_opt.python import mathopt

from funding_lp import build
from gridcap import generate

lp = build(generate("small"))


def try_algorithm(solver: mathopt.SolverType, algorithm: mathopt.LPAlgorithm) -> str:
    try:
        result = mathopt.solve(lp.model, solver, params=mathopt.SolveParameters(lp_algorithm=algorithm))
    except Exception as error:          # OR-Tools 9.15 reports the refusal as this AttributeError
        return f"refused ({type(error).__name__})"
    return result.termination.reason.name


print(f"{'':16}" + "".join(f"{s.name:26}" for s in (mathopt.SolverType.GLOP, mathopt.SolverType.HIGHS,
                                                     mathopt.SolverType.PDLP)))
for algorithm in mathopt.LPAlgorithm:
    row = [try_algorithm(s, algorithm) for s in (mathopt.SolverType.GLOP, mathopt.SolverType.HIGHS,
                                                mathopt.SolverType.PDLP)]
    print(f"{algorithm.name:16}" + "".join(f"{cell:26}" for cell in row))

try:
    mathopt.solve(lp.model, mathopt.SolverType.GLOP,
                  params=mathopt.SolveParameters(lp_algorithm=mathopt.LPAlgorithm.BARRIER))
except Exception as error:
    print(f"GLOP with BARRIER: {type(error).__name__}: {error}")
