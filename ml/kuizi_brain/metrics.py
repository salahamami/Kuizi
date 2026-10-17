"""How we judge the brain (T040, T047, T050).

AUC: how well the model ranks a right answer above a wrong one (0.5 = coin toss, 1 = perfect).
Calibration: when the model says 70 %, are students right about 70 % of the time? Kuizi shows
mastery percentages and a Bac grade estimate, so calibration matters as much as AUC.
"""

import numpy as np
import pandas as pd
from sklearn.metrics import roc_auc_score


def auc(y, p):
    return float(roc_auc_score(y, p))


def accuracy(y, p, threshold=0.5):
    return float(((np.asarray(p) >= threshold) == np.asarray(y)).mean())


def calibration_table(y, p, bins=10):
    """Predictions grouped in bins of equal width, with the observed success rate in each."""
    y, p = np.asarray(y), np.asarray(p)
    edges = np.linspace(0, 1, bins + 1)
    idx = np.clip(np.digitize(p, edges) - 1, 0, bins - 1)
    rows = []
    for b in range(bins):
        sel = idx == b
        if sel.any():
            rows.append((f"{edges[b]:.1f}-{edges[b + 1]:.1f}", p[sel].mean(), y[sel].mean(), int(sel.sum())))
    return pd.DataFrame(rows, columns=["bin", "predicted", "observed", "answers"])


def expected_calibration_error(y, p, bins=10):
    """Average gap between predicted and observed success, weighted by bin size (0 = perfect)."""
    t = calibration_table(y, p, bins)
    return float((t.answers * (t.predicted - t.observed).abs()).sum() / t.answers.sum())


def plot_reliability(ax, y, p, label, marker="o"):
    """Reliability diagram: points on the diagonal mean perfect calibration. Each model gets
    its own marker shape and a label, so the chart does not rely on colour alone."""
    t = calibration_table(y, p)
    ax.plot([0, 1], [0, 1], ls=":", color="#777", lw=1)
    ax.plot(t.predicted, t.observed, marker=marker, label=label)
    ax.set_xlabel("predicted chance of a right answer")
    ax.set_ylabel("observed share of right answers")
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.legend()
    return ax


def report(name, y, p):
    return {"model": name, "AUC": round(auc(y, p), 4), "accuracy": round(accuracy(y, p), 4),
            "ECE": round(expected_calibration_error(y, p), 4), "answers": len(y)}
