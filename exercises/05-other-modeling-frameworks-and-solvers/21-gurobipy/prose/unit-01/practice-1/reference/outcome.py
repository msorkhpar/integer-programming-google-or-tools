from gurobipy import GRB

LIMITS = (GRB.ITERATION_LIMIT, GRB.NODE_LIMIT, GRB.TIME_LIMIT, GRB.SOLUTION_LIMIT, GRB.WORK_LIMIT,
          GRB.MEM_LIMIT, GRB.INTERRUPTED)


def outcome(status: int, sol_count: int) -> str:
    """What the caller does with a solve that ended with this Status and SolCount."""
    if status == GRB.OPTIMAL:
        return "use"
    if status in LIMITS:
        return "use, report gap" if sol_count > 0 else "no plan: limit"
    if status == GRB.INFEASIBLE:
        return "no plan: infeasible"
    if status == GRB.INF_OR_UNBD:
        return "no plan: re-solve with DualReductions=0"
    if status == GRB.UNBOUNDED:
        return "no plan: unbounded"
    return "no plan: solver failure"


if __name__ == "__main__":
    print(outcome(GRB.OPTIMAL, 1), "|", outcome(GRB.TIME_LIMIT, 3), "|", outcome(GRB.INF_OR_UNBD, 0))
