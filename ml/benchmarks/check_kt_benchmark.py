"""Checks that the T040 benchmark compares models fairly. Synthetic data only; runs in seconds.

    cd ml && uv run python benchmarks/check_kt_benchmark.py

1. Evaluation windows predict every answer of a student except the first exactly once, from at
   least half a window of history; training windows use every answer after the first of a window.
2. Every model is causal: changing the answer or the time at step t never changes a prediction
   up to t, and trailing padding never changes a prediction.
3. Length-grouped batches visit every training window once per epoch, and predictions do not
   depend on the batch size.
4. Platt scaling keeps the ranking (same AUC) and the gate rule reads the T047 thresholds.
"""

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import torch

sys.path.insert(0, str(Path(__file__).resolve().parent))
import kt_benchmark as kb  # noqa: E402

MODELS = ["dkt", "sakt", "saint", "akt", "saint_plus", "saint_plus_notime"]


def synthetic_answers(lengths, seed=0):
    rng = np.random.default_rng(seed)
    rows = [(s, i, i % 7, int(rng.integers(0, 2)), 10.0, 30.0) for s, n in enumerate(lengths) for i in range(n)]
    return pd.DataFrame(rows, columns=["student", "item", "kc", "correct", "elapsed_s", "lag_s"])


def check_windows():
    df = synthetic_answers([1, 2, 3, 49, 50, 51, 99, 100, 101, 149, 150, 151, 250, 333])
    for L in (50, 100, 200):
        # evaluation: each answer except a student's first, exactly once
        W = kb.build_windows(df, L, stride=L // 2)
        t = W["target"]
        got = sorted(zip(W["student"][t].tolist(), W["pos"][t].tolist()))
        want = sorted((s, i) for s, g in df.groupby("student") for i in range(1, len(g)))
        assert got == want, f"evaluation windows, L={L}"
        ctx = torch.arange(L).expand_as(W["pos"])[t]
        assert bool((ctx >= torch.minimum(W["pos"][t], torch.tensor(L // 2))).all()), f"history, L={L}"
        # training: every answer after the first of its window
        W = kb.build_windows(df, L)
        got = sorted(zip(W["student"][W["target"]].tolist(), W["pos"][W["target"]].tolist()))
        want = sorted(
            (s, i)
            for s, g in df.groupby("student")
            for i in range(1, len(g))
            if i % L and min(len(g), (i // L + 1) * L) - (i // L) * L >= 2
        )
        assert got == want, f"training windows, L={L}"
    print("1. windows: every test answer predicted once, with at least half a window of history")


def check_causality():
    n_items, n_kc, L = 30, 7, 20
    g = torch.Generator().manual_seed(0)
    b = {
        "item": torch.randint(1, n_items + 1, (2, L), generator=g),
        "kc": torch.randint(1, n_kc + 1, (2, L), generator=g),
        "correct": torch.randint(0, 2, (2, L), generator=g),
        "elapsed": torch.rand(2, L, generator=g),
        "lag": torch.rand(2, L, generator=g),
        "mask": torch.ones(2, L, dtype=torch.bool),
    }
    for name in MODELS:
        torch.manual_seed(0)
        m = kb.make_model(name, n_items, n_kc, L).eval()
        with torch.no_grad():
            p0, _ = m(b)
            assert p0.shape == (2, L - 1), name
            t = 10
            b2 = {k: v.clone() for k, v in b.items()}
            b2["correct"][:, t] = 1 - b2["correct"][:, t]
            b2["elapsed"][:, t] = 0.9
            p1, _ = m(b2)
            assert torch.allclose(p0[:, :t], p1[:, :t], atol=1e-6), f"{name} sees the answer it predicts"
            assert not torch.allclose(p0[:, t:], p1[:, t:], atol=1e-6), f"{name} ignores past answers"
            pt, _ = m({k: v[:, :15] for k, v in b.items()})
            assert torch.allclose(p0[:, :14], pt, atol=1e-5), f"{name} depends on padding"
    print(f"2. causality: {len(MODELS)} models never see the answer they predict and ignore padding")


def check_batches():
    rng = np.random.default_rng(1)
    df = synthetic_answers(rng.integers(2, 160, size=120).tolist(), seed=1)
    n_items, n_kc, L = int(df.item.max()) + 1, int(df.kc.max()) + 1, 100
    W = kb.build_windows(df, L)
    n = W["mask"].shape[0]
    W["wid"] = torch.arange(n)[:, None].expand(n, L).contiguous()
    seen = [i for b in kb.batches(W, 16, shuffle=True, seed=3) for i in b["wid"][:, 0].tolist()]
    assert sorted(seen) == list(range(n)), "a training window is skipped or repeated"
    Wt = kb.build_windows(df, L, stride=L // 2)
    for name in MODELS:
        torch.manual_seed(0)
        m = kb.make_model(name, n_items, n_kc, L)
        p1, p2 = kb.predict(m, Wt, batch_size=64), kb.predict(m, Wt, batch_size=5)
        k1, k2 = np.lexsort((p1["pos"], p1["student"])), np.lexsort((p2["pos"], p2["student"]))
        assert np.allclose(p1["p"][k1], p2["p"][k2], atol=1e-5), f"{name} depends on the batch"
    print("3. batches: every window once per epoch; predictions independent of the batch size")


def check_calibration_and_gate():
    rng = np.random.default_rng(2)
    p = rng.uniform(0.05, 0.95, 4000)
    y = (rng.uniform(size=4000) < p**0.6).astype(int)  # miscalibrated on purpose
    a, b = kb.fit_platt(y, p)
    q = kb.apply_platt(p, a, b)
    assert a > 0 and abs(kb.kb_metrics.auc(y, q) - kb.kb_metrics.auc(y, p)) < 1e-12
    assert kb.kb_metrics.expected_calibration_error(y, q) < kb.kb_metrics.expected_calibration_error(y, p)
    runs = pd.DataFrame(
        [
            (m, f, auc, ece)
            for f in range(3)
            for m, auc, ece in [
                ("dkt", 0.75, 0.01),
                ("good", 0.756, 0.015),
                ("small", 0.753, 0.01),
                ("uncal", 0.77, 0.03),
            ]
        ],
        columns=["model", "fold", "auc", "ece"],
    ).assign(dataset="d", max_len=100)
    slices = runs.assign(slice="all")[["dataset", "model", "max_len", "fold", "slice", "auc"]]
    gate = kb.gate_vs_baseline(runs, slices, "d", 100).set_index("challenger").passes_t047_gate
    assert gate["good"] and not gate["small"] and not gate["uncal"], gate.to_dict()
    print("4. Platt keeps the AUC and lowers ECE; the gate needs +0.005 AUC and ECE within 0.01")


if __name__ == "__main__":
    torch.set_num_threads(1)
    check_windows()
    check_causality()
    check_batches()
    check_calibration_and_gate()
    print("all checks passed")
