from gurobipy import GRB


def outcome(status: int, sol_count: int) -> str:
    """What the caller does with a solve that ended with this Status and SolCount."""
    # TODO: OPTIMAL first, then the limit statuses (SolCount decides), then the "no plan" cases.
    return ""


if __name__ == "__main__":
    print(outcome(GRB.OPTIMAL, 1), "|", outcome(GRB.TIME_LIMIT, 3), "|", outcome(GRB.INF_OR_UNBD, 0))
