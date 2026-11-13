"""One run policy: a single object decides the device, solver, method, threads and tolerances of a solve,
falls back to the CPU, is recorded in the manifest, and says how a GPU result may be used. GridCap is fictional.
"""

import json
from dataclasses import asdict, dataclass

from gpu import describe, gpu_available

from lps import cuopt, gridcap_timing, highs, relative_difference, transport
from milp_gpu import check

GPU_MIN_NONZEROS = 100_000      # below this, the lesson 11.4.3 measurements found the CPU as fast or faster


@dataclass(frozen=True)
class Job:
    name: str
    kind: str                   # "lp" or "milp"
    nonzeros: int
    use: str                    # "plan" (the plan of record), "bound" (an LP bound), or "start" (a starting plan)


@dataclass(frozen=True)
class RunPolicy:
    device: str
    solver: str
    method: str
    threads: int
    tolerance: float            # LP optimality tolerance, or the MILP relative gap
    verify_on_cpu: bool         # a GPU answer is checked on the CPU before anything uses it
    why: str


def decide(job: Job, gpu: bool) -> RunPolicy:
    """The whole policy in one place. Every branch without a GPU is a CPU branch."""
    if job.kind == "milp" and job.use == "plan":
        return RunPolicy("cpu", "highs", "branch-and-bound", 1, 1e-4, False, "the plan of record repeats bit for bit")
    if job.kind == "milp":
        if gpu:
            return RunPolicy("gpu", "cuopt", "milp", 0, 1e-3, True, "a starting plan; 0 threads: cuOpt chooses")
        return RunPolicy("cpu", "highs", "branch-and-bound", 1, 1e-3, False, "no GPU: the CPU solver")
    if job.use == "plan":
        return RunPolicy("cpu", "highs", "simplex", 1, 1e-7, False, "a vertex, repeatable, for the plan of record")
    if gpu and job.nonzeros >= GPU_MIN_NONZEROS:
        return RunPolicy("gpu", "highs", "pdlp", 1, 1e-7, True, "large LP: GPU PDLP, CPU fallback if not Optimal")
    if job.nonzeros >= GPU_MIN_NONZEROS:
        return RunPolicy("cpu", "highs", "ipm", 1, 1e-8, False, "large LP, no GPU: interior point")
    return RunPolicy("cpu", "highs", "simplex", 1, 1e-7, False, "small LP: the CPU is faster")


jobs = [Job("final capital plan", "milp", 2_387, "plan"),
        Job("starting plan for tonight's run", "milp", 2_387, "start"),
        Job("LP relaxation, GridCap small", "lp", 204, "bound"),
        Job("large LP, 300x300 transport", "lp", 180_000, "bound"),
        Job("continuous budget split", "lp", 180_000, "plan")]


def run(job: Job, m: dict) -> dict:
    """Solve under the live policy, fall back to the CPU, verify a GPU answer on the CPU, and return
    what the manifest records: the policy that ran and the result."""
    policy = decide(job, gpu_available())
    if policy.device == "gpu" and policy.solver == "highs":
        result = highs(m, "pdlp", tolerance=policy.tolerance)
        if result["status"] != "Optimal":                       # the fallback: same job, the CPU branch
            policy = decide(job, gpu=False)
            result = highs(m, policy.method, tolerance=policy.tolerance)
    elif policy.device == "gpu":
        result = cuopt(m, settings={"mip_relative_gap": policy.tolerance, "time_limit": 60}, want_x=True)
    elif job.kind == "milp":
        result = highs(m, threads=policy.threads, gap=policy.tolerance)
    else:
        result = highs(m, policy.method, threads=policy.threads, tolerance=policy.tolerance)
    record = {"policy": asdict(policy), "result": {"solver": result["solver"], "status": result["status"],
                                                   "objective": round(result["objective"], 6)}}
    if policy.verify_on_cpu and job.kind == "lp":              # a CPU interior point solve, held to 1e-6
        cpu = highs(m, "ipm")
        record["verified_on_cpu"] = relative_difference(result["objective"], cpu["objective"]) <= 1e-6
    elif policy.verify_on_cpu:                                 # a MILP plan: rows, integrality, and the gap
        cpu = highs(m, threads=1, gap=policy.tolerance)        # to the best bound any solver proved (lesson 11.4.5)
        best = min(result["bound"], cpu["bound"])              # a maximisation: the smallest bound is the tightest
        record["verified_on_cpu"] = check(m, result, best, policy.tolerance)[0]
    return record


def main() -> None:
    print(f"{'job':32s} {'GPU?':5s} {'device':6s} {'solver':6s} {'method':16s} {'thr':>3s} {'tol':>6s}  verify")
    for job in jobs:
        for gpu in (False, True):
            p = decide(job, gpu)
            print(f"{job.name:32s} {str(gpu):5s} {p.device:6s} {p.solver:6s} {p.method:16s} {p.threads:3d} "
                  f"{p.tolerance:6.0e}  {p.verify_on_cpu}")

    small = run(jobs[2], gridcap_timing("small")[0])
    print(json.dumps(small["policy"]))
    print(json.dumps(small["result"]))

    if gpu_available():
        print(describe())
        for job, m in ((jobs[3], transport(300)), (jobs[1], gridcap_timing("medium", integer=True)[0])):
            out = run(job, m)
            print(json.dumps(out["policy"]))
            print(json.dumps(out["result"]), f"verified on the CPU: {out['verified_on_cpu']}")

if __name__ == "__main__":
    main()
