"""The planners' business rules, one function per rule, each adding rows with the names it owns.

Every rule reads the request and the start variables through `built` and adds its rows with
`built.add(name, row)`. A new rule is a new function added to RULES; `build` never changes.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from ortools.math_opt.python import mathopt

if TYPE_CHECKING:
    from .model import Built


def once_or_must(built: Built) -> None:
    """Adds a row `once_<id>` (the project starts at most once) for each discretionary project, and a row `must_<id>` (it starts exactly once) for each must-do project."""
    return None


def alternatives(built: Built) -> None:
    """Adds a row `alt_<group>` per alternative group: the projects of the group start at most once between them."""
    return None


def bundles(built: Built) -> None:
    """Adds a row `bundle_<first>_<other>` for each further member of a bundle: that member is funded exactly when the bundle's first member, in id order, is."""
    return None


def parents(built: Built) -> None:
    """Adds a row `after_<child>_<t>` for each start year t of a child: the child started by t needs its parent started by t minus the lag."""
    return None


def budgets(built: Built) -> None:
    """Adds a row `budget_<y>` per plan year: that year's spend, costs spread over the years of work, within that year's budget."""
    return None


RULES = (once_or_must, alternatives, bundles, parents, budgets)
