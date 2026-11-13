from __future__ import annotations

from ortools.math_opt.python import mathopt
from ortools.math_opt.solvers import highs_pb2


def highs_parameters(seed: int, threads: int, nodes: int) -> mathopt.SolveParameters:
    """Parameters for a HiGHS run that repeats: seed, pinned threads, a node limit."""
    return mathopt.SolveParameters(
        random_seed=seed,
        node_limit=nodes,
        highs=highs_pb2.HighsOptionsProto(int_options={"threads": threads}),
    )


if __name__ == "__main__":
    print(highs_parameters(seed=3, threads=1, nodes=500))
