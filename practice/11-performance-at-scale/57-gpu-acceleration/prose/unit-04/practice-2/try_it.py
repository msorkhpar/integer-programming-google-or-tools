"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")
from manifest import entry

cpu = {"device": "cpu"}
gpu = {"device": "gpu", "name": "Demo Card 42", "compute_capability": "8.6", "driver_cuda": "12.8",
       "cuda_runtime": "12.8.1", "uuid": "GPU-11111111-2222-3333-4444-555555555555"}
result = {"status": "Optimal", "objective": 1_930.5, "x_digest": "7be0", "iterations": 311, "wall_seconds": 0.42}

print("highs simplex on cpu:", entry({"solver": "highs", "method": "simplex", "tolerance": 1e-7, "threads": 1}, result, cpu))
print("highs pdlp on gpu:", entry({"solver": "highs", "method": "pdlp", "tolerance": 1e-6, "threads": 1}, result, gpu))
concurrent = {"solver": "cuopt", "method": "concurrent", "tolerance": 1e-4, "threads": 0}
print("cuopt concurrent, barrier won:", entry(concurrent, {**result, "solved_by": "barrier"}, gpu))
print("cuopt concurrent, no winner reported:", entry(concurrent, result, gpu))
