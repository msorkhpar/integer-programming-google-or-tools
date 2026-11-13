"""Capture a solver's log as a list of lines, and mask the times in it so a page can quote it."""

from __future__ import annotations

import re

from ortools.math_opt.python import mathopt

TIMES = [
    (re.compile(r"\(\d+\.\d+s\)"), "(<t>s)"),                               # GLOP presolve steps
    (re.compile(r"(\s)\d+(\.\d+)?s$"), r"\1<t>s"),                           # HiGHS progress lines
    (re.compile(r"(HiGHS run time\s*:\s*)[\d.]+"), r"\1<t>"),                # HiGHS footer
    (re.compile(r"^time: [\d.e-]+$"), "time: <t>"),                          # GLOP footer
    (re.compile(r"^(\s*\d+\s+[\d.]+\s+)[\d.]+(\s+\|)"), r"\1<t>\2"),         # PDLP table rows
    (re.compile(r"goo\.gle/\S+"), "goo.gle/<link>"),                       # PDLP: a link that varies per run
]


def mask_times(line: str) -> str:
    """Wall-clock times (and PDLP's parameter link) change on every run; the rest of these logs does not."""
    for pattern, replacement in TIMES:
        line = pattern.sub(replacement, line)
    return line


def solve_with_log(model: mathopt.Model, solver: mathopt.SolverType,
                   params: mathopt.SolveParameters | None = None) -> tuple[mathopt.SolveResult, list[str]]:
    """Solve, and keep every log line the solver wrote, in order, in a Python list."""
    lines: list[str] = []
    result = mathopt.solve(model, solver, params=params, msg_cb=lines.extend)
    return result, [mask_times(line) for line in lines]
