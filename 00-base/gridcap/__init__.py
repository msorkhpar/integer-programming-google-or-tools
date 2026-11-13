"""GridCap: a fictional utility's capital portfolio, generated from a size and a seed.

    >>> from gridcap import generate
    >>> tiny = generate("tiny")
    >>> len(tiny.projects)
    8

GridCap is invented for this course. It is not any real utility's data.
"""

from .csvio import load_csv, save_csv
from .generator import DEFAULT_SEED, SIZES, generate
from .portfolio import PROGRAMS, REGIONS, Asset, Portfolio, Project

__all__ = ["Asset", "DEFAULT_SEED", "PROGRAMS", "Portfolio", "Project", "REGIONS", "SIZES", "generate", "load_csv", "save_csv"]
