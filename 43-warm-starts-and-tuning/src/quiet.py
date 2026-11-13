"""Keep what C++ solvers write straight to the process's standard output off a program's output.

The HiGHS bundled in OR-Tools 9.15.6755 can print a stray debug line on a MIP solve, below Python,
where `print` cannot see it, even with no log requested. `muted()` points file descriptor 1 at /dev/null
while a solver runs and flushes C's buffer there before pointing it back. The same helper as
lesson 5.4.1's `quiet.py`.
"""

from __future__ import annotations

import contextlib
import ctypes
import os
import sys
from collections.abc import Iterator


@contextlib.contextmanager
def muted() -> Iterator[None]:
    """Throw away whatever the block writes to standard output, Python's or C's."""
    sys.stdout.flush()
    saved, sink = os.dup(1), os.open(os.devnull, os.O_WRONLY)
    os.dup2(sink, 1)
    try:
        yield
    finally:
        ctypes.CDLL(None).fflush(None)
        os.dup2(saved, 1)
        os.close(saved)
        os.close(sink)
