"""Stub for lesson 14.1.8: the planner as an HTTP service."""

from __future__ import annotations

from fastapi import FastAPI


def create_app(db: str = ":memory:") -> FastAPI:
    return FastAPI(title="Vegetation crew planner")
