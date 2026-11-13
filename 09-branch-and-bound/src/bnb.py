"""LP-based branch-and-bound over a 0-1 selection model, with every step recorded.

Each node is a set of variables held at 0 or 1 (`fixed`). Solving a node means solving the LP
relaxation with those values held (`selection.solve_lp`). The rules the module's lessons teach are
switches here, so one program can compare them on the same model:

* `prune`: drop a node whose LP bound cannot beat the incumbent (lesson 3.2.2);
* `round_bound`: with integer objective coefficients, compare the bound rounded down (lesson 3.2.2);
* `node_rule`: "depth", "best" or "breadth" (lesson 3.2.3);
* `var_rule`: "first", "most" or "strong" (lesson 3.2.3).
"""

from __future__ import annotations

import heapq
import math
from dataclasses import dataclass, field

from selection import LP, Selection, solve_lp

EPS = 1e-6


def fractional(x: dict[str, float]) -> list[str]:
    """The variables whose LP value is not within EPS of a whole number, in model order."""
    return [name for name, v in x.items() if abs(v - round(v)) > EPS]


@dataclass
class Node:
    id: int
    depth: int
    fixed: dict[str, int]
    bound: float                   # the parent's LP value: no plan below this node is worth more
    branch: str = "root"           # the bound change that made this node, e.g. "x_P003 = 1"


@dataclass
class Step:
    node: Node
    lp: LP | None                  # None when the node was pruned before its LP was solved
    action: str
    waiting_bound: float | None = None   # the best bound among the nodes still waiting after this step


@dataclass
class Search:
    value: float | None = None     # the incumbent's value
    plan: list[str] = field(default_factory=list)
    steps: list[Step] = field(default_factory=list)
    lps: int = 0                   # LPs solved, strong-branching trials included
    most_open: int = 0             # the largest number of nodes waiting at once


def can_beat(bound: float, search: Search, round_bound: bool) -> bool:
    """True when a node with this LP bound could still hold a plan better than the incumbent."""
    if search.value is None or bound == math.inf:
        return True
    if round_bound:
        bound = math.floor(bound + EPS)
    return bound > search.value + EPS


def choose_variable(sel: Selection, node: Node, lp: LP, rule: str, search: Search) -> str:
    """The fractional variable to branch on."""
    candidates = fractional(lp.x)
    if rule == "first":
        return candidates[0]
    if rule == "most":
        return max(candidates, key=lambda name: min(lp.x[name], 1 - lp.x[name]))
    if rule == "strong":
        def drop(name: str, value: int) -> float:
            search.lps += 1
            child = solve_lp(sel, {**node.fixed, name: value})
            return math.inf if child.value is None else lp.value - child.value
        return max(candidates, key=lambda name: max(drop(name, 0), EPS) * max(drop(name, 1), EPS))
    raise ValueError(f"unknown variable rule {rule!r}")


class Open:
    """The nodes waiting to be solved, handed out in the order the node rule asks for."""

    def __init__(self, rule: str) -> None:
        self.rule, self.items, self.heap = rule, [], []

    def push(self, node: Node) -> None:
        if self.rule == "best":
            heapq.heappush(self.heap, (-node.bound, node.id, node))
        else:
            self.items.append(node)

    def pop(self) -> Node:
        if self.rule == "best":
            return heapq.heappop(self.heap)[2]
        return self.items.pop() if self.rule == "depth" else self.items.pop(0)

    def bounds(self) -> list[float]:
        return [n.bound for n in self.items] + [-key for key, _, _ in self.heap]

    def __len__(self) -> int:
        return len(self.items) + len(self.heap)


def branch_and_bound(sel: Selection, node_rule: str = "depth", var_rule: str = "first", prune: bool = True,
                     round_bound: bool = False, start: tuple[float, list[str]] | None = None) -> Search:
    search = Search()
    if start:
        search.value, search.plan = start
    waiting, made = Open(node_rule), 1
    waiting.push(Node(0, 0, {}, math.inf))
    while waiting:
        node = waiting.pop()
        if prune and not can_beat(node.bound, search, round_bound):
            search.steps.append(Step(node, None, "pruned before its LP: parent bound cannot beat the incumbent",
                                     max(waiting.bounds(), default=None)))
            continue
        lp = solve_lp(sel, node.fixed)
        search.lps += 1
        if lp.status == "infeasible":
            action = "pruned: infeasible"
        elif prune and not can_beat(lp.value, search, round_bound):
            action = f"pruned: bound {lp.value:,.1f} cannot beat {search.value:,.0f}"
        elif not fractional(lp.x):
            if search.value is None or lp.value > search.value + EPS:
                search.value, search.plan = lp.value, [n for n, v in lp.x.items() if v > 0.5]
                action = f"integral: new incumbent {lp.value:,.0f}"
            else:
                action = f"integral: {lp.value:,.0f} is no better"
        else:
            name = choose_variable(sel, node, lp, var_rule, search)
            action = f"branch on x_{name} = {lp.x[name]:.3f}"
            for value in (0, 1):
                waiting.push(Node(made, node.depth + 1, {**node.fixed, name: value}, lp.value, f"x_{name} = {value}"))
                made += 1
        search.steps.append(Step(node, lp, action, max(waiting.bounds(), default=None)))
        search.most_open = max(search.most_open, len(waiting))
    return search


def show(search: Search) -> None:
    """Print the tree one node per line, indented by depth, in the order the nodes were taken."""
    for step in search.steps:
        lp = "not solved" if step.lp is None else (
            "infeasible" if step.lp.value is None else f"LP {step.lp.value:,.1f}")
        print(f"{step.node.id:>3} {'  ' * step.node.depth}{step.node.branch:<{14 - 2 * step.node.depth + 12}}"
              f"{lp:>12}  {step.action}")
