"""Is there a GPU this program can use? One answer for every lesson, practice and test.

The course runs on the toolchain's CPU image everywhere. A learner who wants the GPU path also has the
optional GPU variant (HiGHS built with CUDA as `highspy`, and NVIDIA cuOpt), and `scripts/runner.py`
starts it only when it is present and Docker reaches a GPU. This module tells a program which of the two
it is running on, so GPU-only checks run on the variant and skip cleanly everywhere else:

```python
from gpu import gpu_available, describe, requires_gpu, run_cuopt

print(describe())                  # "device: CPU (...)" or "device: GPU NVIDIA ... (sm_120), ..."

@requires_gpu()                    # a pytest test that runs only on the GPU variant with a GPU
def test_pdlp_on_the_gpu(): ...
```

`gpu_available()` is True only when BOTH hold: the image is the GPU variant (it carries
`/opt/gpu/variant.json`) and the CUDA driver reports a device. The driver is asked in a child process, so
the caller's own process never initialises CUDA (a forked child of a process that has cannot use it).

cuOpt lives in a venv of its own (`/opt/gpu/cuopt`): its closure pins pandas and numpy versions the course
image cannot hold. `run_cuopt(script, *args)` runs a program with that interpreter, in its own process.
"""

from __future__ import annotations

import functools
import json
import os
import subprocess
import sys
from pathlib import Path

VARIANT_FILE = Path("/opt/gpu/variant.json")

_PROBE = r"""
import ctypes, json
cuda = ctypes.CDLL("libcuda.so.1")
assert cuda.cuInit(0) == 0, "cuInit failed"
count, version = ctypes.c_int(), ctypes.c_int()
assert cuda.cuDeviceGetCount(ctypes.byref(count)) == 0 and count.value > 0, "no CUDA device"
cuda.cuDriverGetVersion(ctypes.byref(version))
device, name = ctypes.c_int(), ctypes.create_string_buffer(256)
cuda.cuDeviceGet(ctypes.byref(device), 0)
cuda.cuDeviceGetName(name, 256, device)
major, minor = ctypes.c_int(), ctypes.c_int()
cuda.cuDeviceGetAttribute(ctypes.byref(major), 75, device)   # CU_DEVICE_ATTRIBUTE_COMPUTE_CAPABILITY_MAJOR
cuda.cuDeviceGetAttribute(ctypes.byref(minor), 76, device)   # CU_DEVICE_ATTRIBUTE_COMPUTE_CAPABILITY_MINOR
print(json.dumps({"devices": count.value, "name": name.value.decode(), "compute_capability": f"{major.value}.{minor.value}",
                  "driver_cuda": f"{version.value // 1000}.{version.value % 1000 // 10}"}))
"""


def variant() -> dict | None:
    """What the GPU variant holds (versions of highspy, CUDA and cuOpt), or None on the CPU image."""
    try:
        return json.loads(VARIANT_FILE.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


@functools.cache
def _device() -> dict | None:
    """The first CUDA device, asked of the driver in a child process; None when there is none."""
    if variant() is None:
        return None
    try:
        done = subprocess.run([sys.executable, "-c", _PROBE], capture_output=True, text=True, timeout=60)
    except subprocess.TimeoutExpired:
        return None
    if done.returncode != 0:
        return None
    return json.loads(done.stdout)


def gpu_available() -> bool:
    """True on the GPU variant with a GPU that Docker passed in; False on the CPU image or with no GPU."""
    return _device() is not None


def device_report() -> dict:
    """Where this program runs, with the versions a GPU result must state."""
    found = _device()
    if found is None:
        held = variant()
        why = "the CPU image" if held is None else "the GPU variant, but no GPU reached the container"
        return {"device": "cpu", "why": why}
    held = variant() or {}
    return {"device": "gpu", **found, "cuda_runtime": held.get("cuda_runtime"), "highspy": held.get("highspy"),
            "cuopt": held.get("cuopt")}


def describe() -> str:
    """One line for a program's output: the device, and for a GPU its name and CUDA versions."""
    report = device_report()
    if report["device"] == "cpu":
        return f"device: CPU ({report['why']})"
    return (f"device: GPU {report['name']} (compute capability {report['compute_capability']}), "
            f"driver CUDA {report['driver_cuda']}, runtime CUDA {report['cuda_runtime']}")


def cuopt_python() -> str | None:
    """The interpreter that has cuOpt, on the GPU variant with a GPU; None elsewhere."""
    held = variant()
    if not gpu_available() or not held or not held.get("cuopt_python"):
        return None
    return held["cuopt_python"] if os.access(held["cuopt_python"], os.X_OK) else None


def run_cuopt(script: str | os.PathLike, *args: str, timeout: float = 600) -> subprocess.CompletedProcess:
    """Run `script` with cuOpt's interpreter, in its own process, and return what it printed."""
    python = cuopt_python()
    if python is None:
        raise RuntimeError("cuOpt needs the GPU variant and a GPU; check gpu_available() first")
    return subprocess.run([python, str(script), *map(str, args)], capture_output=True, text=True, timeout=timeout)


def requires_gpu():
    """A pytest mark: the test runs on the GPU variant with a GPU, and is skipped with a reason elsewhere."""
    import pytest

    return pytest.mark.skipif(not gpu_available(), reason=f"needs a GPU: {device_report().get('why', '')}")
