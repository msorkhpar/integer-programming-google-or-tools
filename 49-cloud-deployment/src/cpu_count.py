"""Lesson 12.5.1: what a process inside a container believes about its CPUs, and how to tell it.

Each child process stands for the container's Python. PYTHON_CPU_COUNT (Python 3.13+) overrides
what os.cpu_count() and os.process_cpu_count() report; CP-SAT's num_workers is set from a setting
instead of being left to count the machine's cores. GridCap is a fictional utility.
"""

import os
import subprocess
import sys

from ortools.sat.python import cp_model

ASK = "import os; print(os.cpu_count(), os.process_cpu_count())"
plain = subprocess.run([sys.executable, "-c", ASK], capture_output=True, text=True).stdout.split()
told = subprocess.run([sys.executable, "-c", ASK], capture_output=True, text=True,
                      env={**os.environ, "PYTHON_CPU_COUNT": "2"}).stdout.split()
print("no override:          cpu_count == process_cpu_count:", plain[0] == plain[1])
print("PYTHON_CPU_COUNT=2:   cpu_count, process_cpu_count =", ", ".join(told))

# A small CP-SAT model: pick at most 3 of 8 crews' jobs, most value first.
model = cp_model.CpModel()
value = [7, 5, 9, 4, 6, 8, 3, 2]
pick = [model.new_bool_var(f"pick_{j}") for j in range(len(value))]
model.add(sum(pick) <= 3)
model.maximize(sum(v * p for v, p in zip(value, pick)))

solver = cp_model.CpSolver()
solver.parameters.num_workers = 2            # from the container's vCPU count, never left at 0
solver.parameters.log_search_progress = True
solver.parameters.log_to_stdout = False
log: list[str] = []
solver.log_callback = log.append
status = solver.solve(model)
started = next(line for line in log if line.startswith("Starting search"))
print("CP-SAT:", solver.status_name(status), "value", int(solver.objective_value), "|",
      started.split(" with ")[1])
