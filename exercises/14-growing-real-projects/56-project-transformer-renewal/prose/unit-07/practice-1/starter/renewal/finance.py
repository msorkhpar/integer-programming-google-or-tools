"""The plan as finance reads it. Stub: the next lesson writes the lines and the report."""

from __future__ import annotations

from .fleet import Transformer
from .request import Plan, Request


def finance_lines(fleet: list[Transformer], request: Request, plan: Plan) -> list:
    """One line per plan year, years with no work included."""
    return []


def finance_report(fleet: list[Transformer], request: Request, plan: Plan) -> str:
    """A Markdown report: the table by year, the totals, and how close the plan is to the best."""
    return ""
