"""`gpu`: one answer to "is there a GPU?", which is False on the CPU image and skips GPU-only tests there."""

from __future__ import annotations

import json
import os

import pytest

import gpu


@pytest.fixture(autouse=True)
def fresh():
    gpu._device.cache_clear()
    yield
    gpu._device.cache_clear()


def test_without_the_variant_there_is_no_gpu_and_the_report_says_cpu(monkeypatch, tmp_path):
    monkeypatch.setattr(gpu, "VARIANT_FILE", tmp_path / "absent.json")
    assert gpu.gpu_available() is False
    assert gpu.device_report() == {"device": "cpu", "why": "the CPU image"}
    assert gpu.describe() == "device: CPU (the CPU image)"
    assert gpu.cuopt_python() is None
    with pytest.raises(RuntimeError, match="GPU variant"):
        gpu.run_cuopt("solve.py")


def test_the_variant_with_no_device_is_still_cpu(monkeypatch, tmp_path):
    held = tmp_path / "variant.json"
    held.write_text(json.dumps({"variant": "optimization-gpu", "cuopt_python": "/opt/gpu/cuopt/bin/python"}))
    monkeypatch.setattr(gpu, "VARIANT_FILE", held)
    monkeypatch.setattr(gpu, "_PROBE", "raise SystemExit(1)")
    assert gpu.gpu_available() is False
    assert gpu.device_report()["why"] == "the GPU variant, but no GPU reached the container"


def test_a_device_the_driver_reports_is_described_with_its_versions(monkeypatch, tmp_path):
    held = tmp_path / "variant.json"
    held.write_text(json.dumps({"variant": "optimization-gpu", "cuda_runtime": "13.3.29", "highspy": "1.14.0"}))
    monkeypatch.setattr(gpu, "VARIANT_FILE", held)
    found = {"devices": 1, "name": "Example GPU", "compute_capability": "12.0", "driver_cuda": "13.2"}
    monkeypatch.setattr(gpu, "_PROBE", f"print({json.dumps(json.dumps(found))})")
    assert gpu.gpu_available() is True
    assert gpu.describe() == ("device: GPU Example GPU (compute capability 12.0), driver CUDA 13.2, "
                              "runtime CUDA 13.3.29")


@gpu.requires_gpu()
def test_a_gpu_only_test_runs_only_where_a_gpu_is():
    assert gpu.gpu_available()
    assert os.environ.get("TOOLCHAIN_VARIANT", "gpu") == "gpu"


def test_the_real_answer_matches_the_image():
    if gpu.variant() is None:
        assert not gpu.gpu_available()
    else:
        assert gpu.device_report()["device"] in ("cpu", "gpu")
