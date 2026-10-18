"""The T040 benchmark's fairness checks (benchmarks/check_kt_benchmark.py) also run in CI.

The script stays the reference (`uv run python benchmarks/check_kt_benchmark.py`); this file only
calls its four checks so a change that breaks the benchmark's fairness fails the pull request.
"""

import importlib.util
from pathlib import Path

import pytest

CHECK_SCRIPT = Path(__file__).resolve().parents[1] / "benchmarks" / "check_kt_benchmark.py"
CHECKS = ["check_windows", "check_causality", "check_batches", "check_calibration_and_gate"]


@pytest.fixture(scope="module")
def checks():
    spec = importlib.util.spec_from_file_location("check_kt_benchmark", CHECK_SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)  # puts benchmarks/ on sys.path and imports kt_benchmark (pyKT)
    return module


@pytest.mark.parametrize("name", CHECKS)
def test_benchmark_check(checks, name):
    getattr(checks, name)()
