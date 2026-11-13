"""Keep what C++ solvers write to the process's standard output off a lesson's printed output.

Some solvers inside OR-Tools 9.15.6755 write to file descriptor 1 directly, below Python: HiGHS run
through the linear solver wrapper prints a banner line, and the HiGHS behind MathOpt can print a
stray debug line on a MIP solve, even with no log requested. Python's `print` cannot see or stop that
output, so these helpers point descriptor 1 somewhere else while a solver runs.
"""

from __future__ import annotations

import contextlib
import ctypes
import os
import sys
import tempfile
from collections.abc import Iterator


@contextlib.contextmanager
def redirected(target_fd: int, fd: int = 1) -> Iterator[None]:
    """Send descriptor `fd` (1, standard output) to `target_fd` inside the block, flushing C's buffer."""
    sys.stdout.flush()
    sys.stderr.flush()
    saved = os.dup(fd)
    os.dup2(target_fd, fd)
    try:
        yield
    finally:
        ctypes.CDLL(None).fflush(None)
        os.dup2(saved, fd)
        os.close(saved)


@contextlib.contextmanager
def muted() -> Iterator[None]:
    """Throw away whatever the block writes to standard output, Python's or C's."""
    sink = os.open(os.devnull, os.O_WRONLY)
    try:
        with redirected(sink):
            yield
    finally:
        os.close(sink)


@contextlib.contextmanager
def captured(lines: list[str], fd: int = 1) -> Iterator[None]:
    """Collect what the block writes to descriptor `fd` (1 by default; 2 is the log) into `lines`."""
    with tempfile.TemporaryFile(mode="w+") as sink:
        with redirected(sink.fileno(), fd):
            yield
        sink.seek(0)
        lines.extend(line.rstrip("\n") for line in sink)
