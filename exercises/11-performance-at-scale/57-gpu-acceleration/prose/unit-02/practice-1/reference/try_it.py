"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")
from fallback import solve_with_fallback


def solver(name, needs_gpu, status=None, fails=False):
    def solve(model):
        if fails:
            raise MemoryError("device out of memory")
        return {"status": status, "objective": 42.0, "by": name}
    return {"name": name, "needs_gpu": needs_gpu, "solve": solve}


chain = [solver("cuopt", True, fails=True), solver("highs-pdlp", True, "Time limit reached"),
         solver("highs-ipm", False, "Optimal"), solver("highs-simplex", False, "Optimal")]

for gpu in (True, False):
    result, log = solve_with_fallback("transport lp", chain, gpu=gpu)
    print(f"gpu={gpu}: answer by", None if result is None else result["by"], "| log:", log)
result, log = solve_with_fallback("transport lp", chain[:2], gpu=True)
print("gpu solvers only, gpu=True: answer", result, "| log:", log)
