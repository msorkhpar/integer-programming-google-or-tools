"""A run manifest that records the device, the method and the tolerance, and a comparison rule that asks for
equal bits only between runs whose manifests promise them.

The manifest follows lesson 10.2.4: inputs, solver, versions, result, and no clock and nothing that names
the machine. GridCap is fictional.
"""

import json
import platform
from importlib.metadata import version

from gpu import device_report, gpu_available

from lps import digest, highs, ortools_pdlp, relative_difference, transport

TOLERANCE = 1e-6


def manifest(m: dict, run: dict, method: str, tolerance: float, threads: int, device: str,
             requested: str | None = None) -> dict:
    """What went in and what came out; `device` is where this solver ran, not what the machine has.
    For a race, `method` is the winner and `requested` is "concurrent"."""
    where = {"device": "cpu"}
    if device == "gpu":
        report = device_report()
        where = {"device": "gpu", "device_name": report["name"], "driver_cuda": report["driver_cuda"],
                 "cuda_runtime": report["cuda_runtime"]}
    if requested is not None:
        where["requested"] = requested
    return {
        "inputs": {"model": digest(m["c"] + m["values"] + m["row_lb"] + m["row_ub"]),
                   "kind": "milp" if any(m["integer"]) else "lp"},
        "solver": {"name": run["solver"].split("-")[0], "method": method, "tolerance": tolerance, "threads": threads,
                   **where},
        "versions": {"python": platform.python_version(), "ortools": version("ortools"), "highspy": version("highspy"),
                     "platform": f"{platform.system()}-{platform.machine()}"},
        "result": {"status": run["status"], "objective": run["objective"], "x": digest(run["x"]),
                   "iterations": run["iterations"]},
    }


def bits_promised(a: dict, b: dict) -> bool:
    """Equal bits are owed only by a repeat (the same solver block and versions) of a run that repeats."""
    if a["solver"] != b["solver"] or a["versions"] != b["versions"]:
        return False
    if a["solver"].get("requested") == "concurrent":                   # a race: the winner can change
        return False
    if a["solver"]["name"] == "cuopt" and a["inputs"]["kind"] == "milp":   # no setting made these repeat
        return False
    return True


def compare(a: dict, b: dict, tol: float = TOLERANCE) -> str:
    """'identical', 'within tolerance', 'different', or 'not comparable' (other inputs)."""
    if a["inputs"] != b["inputs"]:
        return "not comparable"
    if bits_promised(a, b):                                            # a repeat that repeats: every bit
        return "identical" if a["result"] == b["result"] else "different"
    close = relative_difference(a["result"]["objective"], b["result"]["objective"]) <= tol
    return "within tolerance" if close else "different"


def main() -> None:
    m = transport(100)
    pdlp_cpu = manifest(m, ortools_pdlp(m, TOLERANCE), "pdlp", TOLERANCE, 1, "cpu")
    again = manifest(m, ortools_pdlp(m, TOLERANCE), "pdlp", TOLERANCE, 1, "cpu")
    four = manifest(m, ortools_pdlp(m, TOLERANCE, threads=4), "pdlp", TOLERANCE, 4, "cpu")
    ipm = manifest(m, highs(m, "ipm"), "ipm", 1e-8, 1, "cpu")
    print(json.dumps(pdlp_cpu["solver"]))
    print(json.dumps(pdlp_cpu["result"]))
    print(f"OR-Tools PDLP, run again:             {compare(pdlp_cpu, again)}")
    print(f"OR-Tools PDLP, 4 threads against 1:   {compare(pdlp_cpu, four)}")
    print(f"HiGHS interior point against PDLP:    {compare(pdlp_cpu, ipm)}")
    broken = json.loads(json.dumps(again))
    broken["result"]["x"] = "0" * 16
    print(f"a repeat whose plan changed:          {compare(pdlp_cpu, broken)}")
    race = json.loads(json.dumps(again))                 # made-up records: cuOpt's concurrent mode, twice
    race["solver"].update(name="cuopt", method="dual simplex", requested="concurrent", device="gpu")
    race_again = json.loads(json.dumps(race))
    race_again["result"]["x"] = "0" * 16
    print(f"two concurrent runs, plans differ:    {compare(race, race_again)}")
    milp = json.loads(json.dumps(race))                  # made-up records: a cuOpt MILP, twice
    milp["inputs"]["kind"] = "milp"
    milp["solver"].update(method="milp", tolerance=1e-3)
    del milp["solver"]["requested"]
    milp_again = json.loads(json.dumps(milp))
    milp_again["result"]["x"] = "0" * 16
    print(f"two cuOpt MILP runs, plans differ:    {compare(milp, milp_again)}")

    if gpu_available():
        gpu_run = manifest(m, highs(m, "pdlp"), "pdlp", 1e-7, 1, "gpu")
        print(json.dumps(gpu_run["solver"]))
        print(f"HiGHS PDLP on the GPU against OR-Tools PDLP on the CPU: {compare(pdlp_cpu, gpu_run)}, "
              f"objective rel. diff {relative_difference(gpu_run['result']['objective'], pdlp_cpu['result']['objective']):.0e}")


if __name__ == "__main__":
    main()
