"""Shared setup for the brain library tests (T006).

Synthetic data only, CPU only, nothing downloaded: the suite runs in CI and on any PC in under a
minute. Run it from ml/ with `uv run pytest` (add `--cov` for coverage, as CI does).
"""

import os

# Draw figures without a screen (CI runners and WSL have none). Must be set before pyplot loads.
os.environ.setdefault("MPLBACKEND", "Agg")

import matplotlib.pyplot as plt
import pytest
import torch


@pytest.fixture(autouse=True, scope="session")
def _one_cpu_thread():
    """One thread, as the benchmark checks use: results do not depend on the runner's cores."""
    torch.set_num_threads(1)


@pytest.fixture(autouse=True)
def _close_figures():
    yield
    plt.close("all")
