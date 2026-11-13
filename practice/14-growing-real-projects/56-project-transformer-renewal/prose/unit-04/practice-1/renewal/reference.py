"""The reference builder. Stub: the next lesson keeps the plain builder here as the fast one's reference."""

from __future__ import annotations

from ortools.math_opt.python import mathopt

from .fleet import Transformer
from .model import Built
from .request import Request


def build_reference(fleet: list[Transformer], request: Request) -> Built:
    return Built(mathopt.Model(name="renewal"), {}, {})
