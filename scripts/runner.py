"""Run a command inside the course's runner image, offline, from the course root.

    python3 scripts/runner.py python3 scripts/verify_lessons.py 01-optimization-mindset
    python3 scripts/runner.py python3 -m pytest 00-base

The image tag is asked of the toolchain checkout (env TOOLCHAIN, default ../code-server-toolchain),
never typed. The toolchain also chooses between the optimization profile's CPU image and its optional GPU
variant (`consuming/variant.py`): the GPU image runs only when it is present locally and Docker reaches a
GPU with it, and otherwise the CPU image runs, with no error. TOOLCHAIN_VARIANT=cpu or =gpu forces one
(gpu refuses when it cannot run). The GPU variant runs on a Docker engine that reaches a GPU: the
toolchain names it (`docker_host`), by default unix:///var/run/docker.sock when the current context has
no nvidia runtime; TOOLCHAIN_GPU_DOCKER_HOST names another.
The CPU image runs on the current context. The choice is printed on stderr and passed into the container
as TOOLCHAIN_VARIANT; `00-base/gpu.py` tells a program what device it really has.

A Gurobi license is mounted read-only only when GUROBI_LICENSE_FILE (default
.scratch/licenses/gurobi.lic) exists; it is never copied into an image or the repository.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

#: The runtimes the course declares (`corpus.json` `runtimes`), in the form the toolchain takes them. The
#: optimization profile layers on both the python and node bases, and the toolchain refuses a set without node.
RUNTIMES = "node,python"


def toolchain() -> Path:
    return Path(os.environ.get("TOOLCHAIN", ROOT.parent / "code-server-toolchain"))


def image() -> str:
    """The CPU image's tag (or RUNNER_IMAGE), whatever the choice."""
    if os.environ.get("RUNNER_IMAGE"):
        return os.environ["RUNNER_IMAGE"]
    return subprocess.run(
        [sys.executable, str(toolchain() / "docker/profile_packages/package_build.py"), "--root", str(toolchain()),
         "--profile", "optimization", "--image", "runner", "--runtimes", RUNTIMES, "--print-tag"],
        check=True, capture_output=True, text=True).stdout.strip()


def choose() -> dict:
    """`{"variant", "image", "docker_args", "reason"}`: the toolchain's choice between CPU and GPU images."""
    forced = os.environ.get("TOOLCHAIN_VARIANT", "auto")
    if os.environ.get("RUNNER_IMAGE"):
        gpu = forced == "gpu"
        return {"variant": "gpu" if gpu else "cpu", "image": os.environ["RUNNER_IMAGE"],
                "docker_args": ["--gpus", "all"] if gpu else [],
                "docker_host": os.environ.get("TOOLCHAIN_GPU_DOCKER_HOST") if gpu else None, "reason": "RUNNER_IMAGE"}
    chooser = toolchain() / "consuming/variant.py"
    if not chooser.is_file():
        if forced == "gpu":
            raise SystemExit("runner: TOOLCHAIN_VARIANT=gpu, and the toolchain has no GPU variant chooser")
        return {"variant": "cpu", "image": image(), "docker_args": [], "docker_host": None,
                "reason": "the toolchain has no variant chooser"}
    done = subprocess.run(
        [sys.executable, str(chooser), "--root", str(toolchain()), "--profile", "optimization", "--image", "runner",
         "--runtimes", RUNTIMES, "--choose"], capture_output=True, text=True)
    if done.returncode != 0:
        raise SystemExit(f"runner: {done.stderr.strip()}")
    return json.loads(done.stdout)


def argv(command: list[str], chosen: dict | None = None) -> list[str]:
    chosen = chosen or choose()
    args = ["docker", "run", "--rm", "--network", "none", "--user", f"{os.getuid()}:{os.getgid()}",
            "-e", "HOME=/tmp", "-e", "PYTHONDONTWRITEBYTECODE=1", "-e", "MPLBACKEND=Agg",
            "-v", f"{ROOT}:/course", "-w", "/course"]
    license_file = Path(os.environ.get("GUROBI_LICENSE_FILE", ROOT / ".scratch/licenses/gurobi.lic"))
    if license_file.is_file():
        args += ["-v", f"{license_file.resolve()}:/licenses/gurobi.lic:ro", "-e", "GRB_LICENSE_FILE=/licenses/gurobi.lic"]
    args += [*chosen["docker_args"], "-e", f"TOOLCHAIN_VARIANT={chosen['variant']}"]
    return args + [chosen["image"]] + command


def main() -> int:
    chosen = choose()
    host = chosen.get("docker_host")
    where = f" on {host}" if host else ""
    print(f"runner: {chosen['variant']} image {chosen['image']}{where} ({chosen['reason']})", file=sys.stderr)
    env = dict(os.environ, DOCKER_HOST=host) if host else None
    return subprocess.run(argv(sys.argv[1:], chosen), env=env).returncode


if __name__ == "__main__":
    sys.exit(main())
