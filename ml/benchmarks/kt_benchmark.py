"""T040 knowledge-tracing benchmark: DKT, SAKT, SAINT, AKT and SAINT+ on public and simulated data.

Run from ml/ (see ml/benchmarks/README.md):

    uv run python benchmarks/kt_benchmark.py --mode quick    # a few minutes, checks that everything runs
    uv run python benchmarks/kt_benchmark.py --mode full     # the numbers reported in ADR 0007

Protocol
- Students are split into 5 folds with a fixed seed; a run trains on 4 folds (10 % of those
  students held out for early stopping) and tests on the 5th. Splits are by student, never by
  answer, so test students are people the model has never seen.
- Every model sees the same windows: each student's answers are cut into non-overlapping
  windows of `max_len` answers for training. For validation and test, windows overlap by half
  (stride max_len / 2) and each answer is predicted exactly once, from at least max_len / 2 earlier
  answers when the student has them, as the online sequence builder (T048) will do. The first
  answer of a student is never predicted (there is no history). The test predictions are
  therefore identical across models and lengths, which makes the comparison fair.
- Metrics: AUC, accuracy (threshold 0.5), ECE (10 equal-width bins), and AUC / ECE per slice
  (position in the student's history; accommodation groups on the simulator).
- CPU inference latency: one forward pass over a full window of max_len answers predicts the
  next answer of each student in the batch; reported in ms per prediction at batch 1 and 64.
  GPU latency is pending (no GPU before the cloud, S8+) and is written as empty, not invented.

Models: DKT, SAKT, SAINT and AKT come from pyKT (pykt-toolkit); pyKT has no SAINT+, so SAINT+ is
kuizi_brain.models.SaintPlus (T238). Every run is logged to MLflow with its seed, data source and
code version (local server from `make up` when it is reachable, otherwise a git-ignored local
store in ml/benchmarks/mlruns).
"""

from __future__ import annotations

import argparse
import contextlib
import hashlib
import io
import json
import os
import platform
import subprocess
import sys
import time
import urllib.request
from concurrent.futures import ProcessPoolExecutor, as_completed
from functools import lru_cache
from pathlib import Path

import numpy as np
import pandas as pd
import torch
import torch.nn.functional as F
from torch import nn

HERE = Path(__file__).resolve().parent
ML_DIR = HERE.parent
REPO_DIR = ML_DIR.parent
if str(ML_DIR) not in sys.path:
    sys.path.insert(0, str(ML_DIR))

from kuizi_brain import data as kb_data  # noqa: E402
from kuizi_brain import metrics as kb_metrics  # noqa: E402
from kuizi_brain.models import SaintPlus  # noqa: E402

RESULTS_DIR = HERE / "results"
FOLD_SEED = 2026          # assigns students to folds; never change it between runs you compare
N_FOLDS = 5

# ---------------------------------------------------------------------------
# Configuration: quick mode checks that everything runs, full mode gives the reported numbers
# ---------------------------------------------------------------------------

MODELS = ["dkt", "sakt", "saint", "akt", "saint_plus"]
MODEL_LABELS = {
    "dkt": "DKT (pyKT)",
    "sakt": "SAKT (pyKT)",
    "saint": "SAINT (pyKT)",
    "akt": "AKT (pyKT)",
    "saint_plus": "SAINT+ (kuizi_brain)",
    "saint_plus_notime": "SAINT+ without time (kuizi_brain)",
    "saint_plus_fairtime": "SAINT+ time / multiplier (kuizi_brain)",
}

MODES = {
    "quick": {
        "folds": [0],
        "max_epochs": 2,
        "patience": 1,
        "assist2009": {"max_students": 600, "lengths": [100], "main_length": 100,
                       "models": MODELS, "main_only_models": []},
        "simulated": None,
        "latency_iters": {1: 20, 64: 5},
    },
    "full": {
        "folds": [0, 1, 2],
        "max_epochs": 12,
        "patience": 2,
        "assist2009": {"max_students": None, "lengths": [50, 100, 200], "main_length": 100,
                       "models": MODELS, "main_only_models": ["saint_plus_notime"]},
        "simulated": {"n_students": 600, "answers_per_student": 120, "lengths": [100],
                      "main_length": 100, "models": MODELS,
                      "main_only_models": ["saint_plus_notime", "saint_plus_fairtime"]},
        "latency_iters": {1: 200, 64: 30},
    },
}

HYPER = {"d": 64, "heads": 4, "dropout": 0.2, "lr": 1e-3, "batch_size": 64, "clip": 1.0}

DATA_SOURCES = {
    "assist2009": {
        "name": "ASSISTments 2009-2010 skill builder (corrected, collapsed)",
        "url": "https://sites.google.com/site/assistmentsdata/home/2009-2010-assistment-data/skill-builder-data-2009-2010",
        "terms": "Public research data; cite the URL above and Feng, Heffernan & Koedinger (2009).",
        "file": kb_data.ASSIST2009_FILE,
        "sha256": kb_data.ASSIST2009_SHA256,
    },
    "simulated": {
        "name": "Simulated Bac Physics students (kuizi_brain.data.simulate_students, seed 7)",
        "url": "ml/kuizi_brain/data.py",
        "terms": "Synthetic, no real person behind it.",
    },
}


# ---------------------------------------------------------------------------
# Data: load, split by student, cut into windows
# ---------------------------------------------------------------------------

@lru_cache(maxsize=None)
def load_dataset(name: str, mode: str) -> pd.DataFrame:
    """One row per answer, sorted by student then time. Cached per process. df.attrs holds the
    vocabulary sizes of the whole dataset (n_items, n_kc), also when students are subsampled."""
    cfg = MODES[mode][name]
    if name == "assist2009":
        df = kb_data.load_assist2009()
        n_items, n_kc = int(df.item.max()) + 1, int(df.kc.max()) + 1
        if cfg["max_students"]:
            rng = np.random.default_rng(FOLD_SEED)
            keep = rng.choice(np.sort(df.student.unique()), size=cfg["max_students"], replace=False)
            df = df[df.student.isin(keep)].reset_index(drop=True)
    elif name == "simulated":
        df = kb_data.simulate_students(n_students=cfg["n_students"],
                                       answers_per_student=cfg["answers_per_student"], seed=7)
        n_items, n_kc = int(df.attrs["n_items"]), int(df.attrs["n_kc"])
        df = df.sort_values(["student", "t"], kind="stable").reset_index(drop=True)
    else:
        raise ValueError(name)
    df.attrs = {"n_items": n_items, "n_kc": n_kc}
    return df


def vocab_sizes(name: str, mode: str) -> tuple[int, int]:
    """Number of items and concepts in the whole dataset (ids start at 0 in the loaders)."""
    df = load_dataset(name, mode)
    return df.attrs["n_items"], df.attrs["n_kc"]


def student_folds(students: np.ndarray, n_folds: int = N_FOLDS, seed: int = FOLD_SEED) -> dict:
    perm = np.random.default_rng(seed).permutation(np.sort(students))
    return {int(s): i % n_folds for i, s in enumerate(perm)}


def split_fold(df: pd.DataFrame, fold: int, valid_share: float = 0.1):
    """Train / validation / test by student. Test = one fold; validation = 10 % of the rest."""
    folds = student_folds(df.student.unique())
    f = df.student.map(folds).to_numpy()
    rest = np.sort(df.student[f != fold].unique())
    rng = np.random.default_rng(FOLD_SEED + 100 + fold)
    valid = set(rng.choice(rest, size=max(1, int(len(rest) * valid_share)), replace=False).tolist())
    is_test = f == fold
    is_valid = df.student.isin(valid).to_numpy() & ~is_test
    return (df[~is_test & ~is_valid].reset_index(drop=True), df[is_valid].reset_index(drop=True),
            df[is_test].reset_index(drop=True))


def build_windows(df: pd.DataFrame, max_len: int, stride: int | None = None, fair_time: bool = False) -> dict:
    """Cut each student's answers into windows of max_len (0 = padding for item and concept ids).

    stride=None: training windows, non-overlapping, every answer after the first of a window is
    a target. stride=S: evaluation windows starting at 0, S, 2S...; the first window predicts its
    answers 1..max_len-1, each later window only its last S answers, so every answer of a student
    (except the very first) is predicted once, with at least max_len - S earlier answers.
    Time features use the same scaling as kuizi_brain.models.make_windows.
    """
    student = df.student.to_numpy()
    starts = np.flatnonzero(np.r_[True, student[1:] != student[:-1]])
    ends = np.r_[starts[1:], len(df)]
    elapsed = df.elapsed_s.to_numpy(dtype=float)
    if fair_time and "time_multiplier" in df:
        elapsed = elapsed / df.time_multiplier.to_numpy(dtype=float)
    lag = df.lag_s.to_numpy(dtype=float) if "lag_s" in df else np.zeros(len(df))
    cols = {
        "item": df.item.to_numpy() + 1,
        "kc": df.kc.to_numpy() + 1,
        "correct": df.correct.to_numpy(),
        "elapsed": np.log1p(elapsed) / 5.0,
        "lag": np.log1p(lag / 60.0) / 8.0,
        "accommodation": (df.time_multiplier.to_numpy() > 1) if "time_multiplier" in df else np.zeros(len(df), bool),
        "assistive": df.assistive.to_numpy().astype(bool) if "assistive" in df else np.zeros(len(df), bool),
    }
    spans = []   # (row offset of window start, n real answers, first target position in window)
    for a, b in zip(starts, ends):
        n = b - a
        if n < 2:
            continue
        if stride is None:
            for s in range(0, n, max_len):
                if n - s >= 2:
                    spans.append((a + s, min(max_len, n - s), 1, s))
        else:
            spans.append((a, min(max_len, n), 1, 0))
            k = 1
            while k * stride + max_len - stride < n:
                s = k * stride
                spans.append((a + s, min(max_len, n - s), max_len - stride, s))
                k += 1
    W = len(spans)
    out = {k: np.zeros((W, max_len), dtype=v.dtype if v.dtype != np.int64 else np.int64) for k, v in cols.items()}
    out["mask"] = np.zeros((W, max_len), dtype=bool)
    out["target"] = np.zeros((W, max_len), dtype=bool)
    out["student"] = np.zeros((W, max_len), dtype=np.int64)
    out["pos"] = np.zeros((W, max_len), dtype=np.int64)
    for w, (row, n, first, offset) in enumerate(spans):
        for k, v in cols.items():
            out[k][w, :n] = v[row:row + n]
        out["mask"][w, :n] = True
        out["target"][w, first:n] = True
        out["student"][w, :n] = student[row]
        out["pos"][w, :n] = np.arange(offset, offset + n)
    t = {k: torch.from_numpy(v) for k, v in out.items()}
    for k in ("item", "kc", "correct", "student", "pos"):
        t[k] = t[k].long()
    for k in ("elapsed", "lag"):
        t[k] = t[k].float()
    return t


def batches(windows: dict, batch_size: int, shuffle: bool, seed: int = 0):
    n = windows["mask"].shape[0]
    order = torch.randperm(n, generator=torch.Generator().manual_seed(seed)) if shuffle else torch.arange(n)
    for i in range(0, n, batch_size):
        idx = order[i:i + batch_size]
        b = {k: v[idx] for k, v in windows.items()}
        # trim trailing padding shared by the whole batch (right padding + causal models = safe)
        real = int(b["mask"].sum(1).max())
        yield {k: v[:, :max(real, 2)] for k, v in b.items()}


# ---------------------------------------------------------------------------
# Models: one interface. forward(batch) -> (P(correct) for positions 1..L-1, extra loss)
# ---------------------------------------------------------------------------

@contextlib.contextmanager
def quiet():
    with contextlib.redirect_stdout(io.StringIO()):
        yield


class PyktDKT(nn.Module):
    """pyKT DKT: an LSTM over (concept, answer) pairs; reads the concept-level prediction."""

    def __init__(self, n_items, n_kc, max_len, d, heads, dropout):
        super().__init__()
        from pykt.models.dkt import DKT
        self.net = DKT(num_c=n_kc + 1, emb_size=d, dropout=dropout)

    def forward(self, b):
        c, r = b["kc"], b["correct"]
        y = self.net(c[:, :-1], r[:, :-1])
        return y.gather(2, c[:, 1:, None]).squeeze(2), 0.0


class PyktSAKT(nn.Module):
    """pyKT SAKT: the next concept attends to past (concept, answer) interactions."""

    def __init__(self, n_items, n_kc, max_len, d, heads, dropout):
        super().__init__()
        from pykt.models.sakt import SAKT
        self.net = SAKT(num_c=n_kc + 1, seq_len=max_len, emb_size=d, num_attn_heads=heads,
                        dropout=dropout, num_en=2)

    def forward(self, b):
        c, r = b["kc"], b["correct"]
        return self.net(c[:, :-1], r[:, :-1], c[:, 1:]), 0.0


class PyktSAINT(nn.Module):
    """pyKT SAINT: encoder over items + concepts, decoder over previous answers."""

    def __init__(self, n_items, n_kc, max_len, d, heads, dropout):
        super().__init__()
        from pykt.models.saint import SAINT
        with quiet():
            self.net = SAINT(num_q=n_items + 1, num_c=n_kc + 1, seq_len=max_len, emb_size=d,
                             num_attn_heads=heads, dropout=dropout, n_blocks=2)

    def forward(self, b):
        return self.net(b["item"], b["kc"], b["correct"][:, :-1])[:, 1:], 0.0


class PyktAKT(nn.Module):
    """pyKT AKT: monotonic attention with distance decay and a Rasch item-difficulty scalar."""

    def __init__(self, n_items, n_kc, max_len, d, heads, dropout):
        super().__init__()
        from pykt.models.akt import AKT
        self.net = AKT(n_question=n_kc + 1, n_pid=n_items + 1, d_model=d, n_blocks=1, dropout=dropout,
                       num_attn_heads=heads)

    def forward(self, b):
        p, reg = self.net(b["kc"], b["correct"], b["item"])
        return p[:, 1:], reg


class KuiziSaintPlus(nn.Module):
    """kuizi_brain SAINT+: SAINT plus previous elapsed time and current lag time in the decoder."""

    def __init__(self, n_items, n_kc, max_len, d, heads, dropout, use_time=True):
        super().__init__()
        self.net = SaintPlus(n_items, n_kc, d=d, heads=heads, layers=2, max_len=max_len, dropout=dropout,
                             use_time=use_time)

    def forward(self, b):
        return torch.sigmoid(self.net(b)[:, 1:]), 0.0


def make_model(name: str, n_items: int, n_kc: int, max_len: int) -> nn.Module:
    h = HYPER
    args = (n_items, n_kc, max_len, h["d"], h["heads"], h["dropout"])
    if name == "dkt":
        return PyktDKT(*args)
    if name == "sakt":
        return PyktSAKT(*args)
    if name == "saint":
        return PyktSAINT(*args)
    if name == "akt":
        return PyktAKT(*args)
    if name in ("saint_plus", "saint_plus_fairtime"):
        return KuiziSaintPlus(*args)
    if name == "saint_plus_notime":
        return KuiziSaintPlus(*args, use_time=False)
    raise ValueError(name)


def count_parameters(model: nn.Module) -> int:
    return sum(p.numel() for p in model.parameters() if p.requires_grad)


# ---------------------------------------------------------------------------
# Training and evaluation
# ---------------------------------------------------------------------------

def bce(p, y):
    return F.binary_cross_entropy(p.clamp(1e-6, 1 - 1e-6), y.float())


@torch.no_grad()
def predict(model: nn.Module, windows: dict, batch_size: int = 128) -> dict:
    """Predictions on every target answer, with the columns the slices need."""
    model.eval()
    out = {k: [] for k in ("y", "p", "student", "pos", "accommodation", "assistive")}
    for b in batches(windows, batch_size, shuffle=False):
        p, _ = model(b)
        sel = b["target"][:, 1:]
        out["p"].append(p[sel].double())
        out["y"].append(b["correct"][:, 1:][sel])
        for k in ("student", "pos", "accommodation", "assistive"):
            out[k].append(b[k][:, 1:][sel])
    return {k: torch.cat(v).numpy() for k, v in out.items()}


def slice_masks(pred: dict, dataset: str) -> dict:
    pos = pred["pos"]
    s = {"answers 2-10": pos < 10, "answers 11-50": (pos >= 10) & (pos < 50), "answers 51+": pos >= 50}
    if dataset == "simulated":
        s["no accommodation"] = ~pred["accommodation"]
        s["extra time (x1.33 or x1.5)"] = pred["accommodation"]
        s["assistive mode"] = pred["assistive"]
    return s


def scores(y, p) -> dict:
    return {"auc": kb_metrics.auc(y, p), "accuracy": kb_metrics.accuracy(y, p),
            "ece": kb_metrics.expected_calibration_error(y, p), "n_predictions": int(len(y))}


def run_job(job: dict) -> dict:
    """Train one model on one fold and length, test it, return metrics. Runs in a worker process."""
    torch.set_num_threads(job["threads"])
    seed = job["seed"]
    torch.manual_seed(seed)
    np.random.seed(seed)
    t0 = time.time()
    df = load_dataset(job["dataset"], job["mode"])
    n_items, n_kc = vocab_sizes(job["dataset"], job["mode"])
    train_df, valid_df, test_df = split_fold(df, job["fold"])
    L = job["max_len"]
    fair = job["model"] == "saint_plus_fairtime"
    W_train = build_windows(train_df, L, fair_time=fair)
    W_valid = build_windows(valid_df, L, stride=L // 2, fair_time=fair)
    W_test = build_windows(test_df, L, stride=L // 2, fair_time=fair)
    torch.manual_seed(seed)
    model = make_model(job["model"], n_items, n_kc, L)
    opt = torch.optim.Adam(model.parameters(), lr=HYPER["lr"])
    best_auc, best_state, best_epoch, history = -1.0, None, 0, []
    t_train = time.time()
    for epoch in range(job["max_epochs"]):
        model.train()
        total, count = 0.0, 0
        for b in batches(W_train, HYPER["batch_size"], shuffle=True, seed=seed * 1000 + epoch):
            p, extra = model(b)
            sel = b["mask"][:, 1:]
            loss = bce(p[sel], b["correct"][:, 1:][sel]) + extra
            opt.zero_grad()
            loss.backward()
            nn.utils.clip_grad_norm_(model.parameters(), HYPER["clip"])
            opt.step()
            total += float(loss.detach()) * int(sel.sum())
            count += int(sel.sum())
        v = predict(model, W_valid)
        v_auc = kb_metrics.auc(v["y"], v["p"])
        history.append({"epoch": epoch + 1, "train_loss": total / count, "valid_auc": v_auc})
        if v_auc > best_auc:
            best_auc, best_epoch = v_auc, epoch + 1
            best_state = {k: t.detach().clone() for k, t in model.state_dict().items()}
        elif epoch + 1 - best_epoch >= job["patience"]:
            break
    train_s = time.time() - t_train
    model.load_state_dict(best_state)
    pred = predict(model, W_test)
    res = {k: job[k] for k in ("dataset", "model", "max_len", "fold", "seed", "mode")}
    res.update(scores(pred["y"], pred["p"]))
    res.update({"valid_auc": best_auc, "best_epoch": best_epoch, "epochs_run": len(history),
                "train_seconds": round(train_s, 1), "job_seconds": round(time.time() - t0, 1),
                "parameters": count_parameters(model), "n_items": n_items, "n_kc": n_kc,
                "train_students": int(train_df.student.nunique()), "test_students": int(test_df.student.nunique()),
                "train_answers": len(train_df), "test_answers": len(test_df)})
    slices = []
    for name, m in slice_masks(pred, job["dataset"]).items():
        if m.sum() > 0 and len(np.unique(pred["y"][m])) == 2:
            slices.append({**{k: res[k] for k in ("dataset", "model", "max_len", "fold")},
                           "slice": name, **scores(pred["y"][m], pred["p"][m])})
    calib = kb_metrics.calibration_table(pred["y"], pred["p"])
    calib = calib.assign(**{k: res[k] for k in ("dataset", "model", "max_len", "fold")}).to_dict("records")
    return {"run": res, "slices": slices, "calibration": calib, "history": history}


# ---------------------------------------------------------------------------
# CPU inference latency
# ---------------------------------------------------------------------------

@torch.no_grad()
def measure_latency(model_name: str, n_items: int, n_kc: int, max_len: int, batch: int, threads: int,
                    iters: int) -> dict:
    """ms per forward pass over full windows of max_len answers; one pass predicts the next
    answer of each of the `batch` students. Weights are freshly initialised: compute time does
    not depend on their values."""
    torch.set_num_threads(threads)
    torch.manual_seed(0)
    model = make_model(model_name, n_items, n_kc, max_len).eval()
    g = torch.Generator().manual_seed(0)
    b = {
        "item": torch.randint(1, n_items + 1, (batch, max_len), generator=g),
        "kc": torch.randint(1, n_kc + 1, (batch, max_len), generator=g),
        "correct": torch.randint(0, 2, (batch, max_len), generator=g),
        "elapsed": torch.rand(batch, max_len, generator=g),
        "lag": torch.rand(batch, max_len, generator=g),
        "mask": torch.ones(batch, max_len, dtype=torch.bool),
    }
    with torch.inference_mode():
        for _ in range(max(3, iters // 10)):
            model(b)
        times = []
        for _ in range(iters):
            t = time.perf_counter()
            model(b)
            times.append((time.perf_counter() - t) * 1000)
    times = np.array(times)
    return {"model": model_name, "max_len": max_len, "batch": batch, "threads": threads, "device": "cpu",
            "iters": iters, "ms_per_call_median": float(np.median(times)),
            "ms_per_call_p95": float(np.percentile(times, 95)),
            "ms_per_prediction": float(np.median(times) / batch), "parameters": count_parameters(model)}


# ---------------------------------------------------------------------------
# Provenance and MLflow
# ---------------------------------------------------------------------------

def sha256_file(path: Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def code_version() -> dict:
    def git(*args):
        try:
            return subprocess.run(["git", *args], cwd=REPO_DIR, capture_output=True, text=True,
                                  timeout=10).stdout.strip()
        except (OSError, subprocess.SubprocessError):
            return ""
    files = [HERE / "kt_benchmark.py"] + sorted((ML_DIR / "kuizi_brain").glob("*.py"))
    h = hashlib.sha256()
    for f in files:
        h.update(f.read_bytes())
    return {"git_commit": git("rev-parse", "HEAD"), "git_branch": git("rev-parse", "--abbrev-ref", "HEAD"),
            "git_dirty": bool(git("status", "--porcelain", "--", "ml/")),
            "code_sha256": h.hexdigest()}


def environment() -> dict:
    import importlib.metadata as md
    return {"python": platform.python_version(), "platform": platform.platform(),
            "processor": platform.processor() or platform.machine(), "cpu_count": os.cpu_count(),
            "torch": torch.__version__, "pykt_toolkit": md.version("pykt-toolkit"),
            "numpy": np.__version__, "pandas": pd.__version__, "cuda_available": torch.cuda.is_available()}


def read_env_file() -> dict:
    env = {}
    for name in (".env",):
        path = REPO_DIR / name
        if path.exists():
            for line in path.read_text().splitlines():
                if "=" in line and not line.lstrip().startswith("#"):
                    k, v = line.split("=", 1)
                    env[k.strip()] = v.strip()
    return env


def mlflow_setup(choice: str):
    """Returns the mlflow module ready to log, or None. 'auto' uses MLFLOW_TRACKING_URI (from the
    environment or .env) when the server answers, else a local file store in benchmarks/mlruns."""
    if choice == "off":
        return None
    try:
        import mlflow
    except ImportError:
        print("MLflow is not installed; runs are not logged")
        return None
    uri = os.environ.get("MLFLOW_TRACKING_URI") or read_env_file().get("MLFLOW_TRACKING_URI")
    target = None
    if uri and uri.startswith("http"):
        try:
            urllib.request.urlopen(uri.rstrip("/") + "/health", timeout=3)
            target = uri
        except OSError:
            print(f"MLflow server {uri} is not reachable (is `make up` running?); logging locally")
    if target is None:
        if choice == "server":
            raise SystemExit("--mlflow server: no reachable MLflow server")
        os.environ.setdefault("MLFLOW_ALLOW_FILE_STORE", "true")
        target = (HERE / "mlruns").as_uri()
    os.environ.setdefault("MLFLOW_DISABLE_AGENT_HINT", "1")
    mlflow.set_tracking_uri(target)
    mlflow.set_experiment("t040-kt-benchmark")
    print(f"MLflow tracking: {target}")
    return mlflow


def mlflow_log(mlflow, out: dict, provenance: dict):
    if mlflow is None:
        return
    r = out["run"]
    src = DATA_SOURCES[r["dataset"]]
    with mlflow.start_run(run_name=f"{r['dataset']}-{r['model']}-L{r['max_len']}-fold{r['fold']}"):
        mlflow.log_params({"model": r["model"], "implementation": MODEL_LABELS[r["model"]], "dataset": r["dataset"],
                           "max_len": r["max_len"], "fold": r["fold"], "seed": r["seed"], "mode": r["mode"],
                           "fold_seed": FOLD_SEED, "n_folds": N_FOLDS, **HYPER,
                           "max_epochs": provenance["config"]["max_epochs"],
                           "patience": provenance["config"]["patience"]})
        mlflow.set_tags({"ticket": "T040", "data_source": src["name"], "data_url": src["url"],
                         "data_sha256": provenance["data_sha256"].get(r["dataset"], "synthetic"),
                         **{f"code_{k}": str(v) for k, v in provenance["code"].items()},
                         **{f"env_{k}": str(v) for k, v in provenance["environment"].items()}})
        mlflow.log_metrics({k: float(r[k]) for k in ("auc", "accuracy", "ece", "valid_auc", "best_epoch",
                                                       "train_seconds", "parameters", "n_predictions")})
        for s in out["slices"]:
            key = "".join(ch if ch.isalnum() else "_" for ch in s["slice"]).strip("_")
            mlflow.log_metrics({f"slice_{key}_auc": s["auc"], f"slice_{key}_ece": s["ece"]})
        for h in out["history"]:
            mlflow.log_metrics({"train_loss": h["train_loss"], "valid_auc_epoch": h["valid_auc"]}, step=h["epoch"])


# ---------------------------------------------------------------------------
# Summary and the T047 gate rule
# ---------------------------------------------------------------------------

GATE = {"auc_gain": 0.005, "slice_drop": 0.01, "ece_worse": 0.01}


def gate_vs_baseline(runs: pd.DataFrame, slices: pd.DataFrame, dataset: str, max_len: int,
                     baseline: str = "dkt") -> pd.DataFrame:
    """T047 rule, on fold-paired differences against the baseline: a challenger is better only if
    mean AUC gain >= +0.005, no slice AUC down by more than 0.01, ECE not worse by more than 0.01."""
    r = runs[(runs.dataset == dataset) & (runs.max_len == max_len)]
    if baseline not in set(r.model):
        return pd.DataFrame()
    auc = r.pivot_table(index="fold", columns="model", values="auc")
    ece = r.pivot_table(index="fold", columns="model", values="ece")
    s = slices[(slices.dataset == dataset) & (slices.max_len == max_len)]
    s_auc = s.pivot_table(index=["slice", "fold"], columns="model", values="auc") if len(s) else None
    rows = []
    for model in auc.columns:
        if model == baseline:
            continue
        folds = auc[[model, baseline]].dropna().index
        d_auc = auc.loc[folds, model] - auc.loc[folds, baseline]
        d_ece = ece.loc[folds, model] - ece.loc[folds, baseline]
        worst_slice, worst = None, np.nan
        if s_auc is not None and model in s_auc:
            per_slice = (s_auc[model] - s_auc[baseline]).dropna().groupby(level="slice").mean()
            if len(per_slice):
                worst_slice, worst = per_slice.idxmin(), float(per_slice.min())
        passed = (d_auc.mean() >= GATE["auc_gain"]) and not (worst < -GATE["slice_drop"]) \
            and (d_ece.mean() <= GATE["ece_worse"])
        rows.append({"dataset": dataset, "max_len": max_len, "challenger": model, "baseline": baseline,
                     "folds": len(folds), "delta_auc_mean": d_auc.mean(),
                     "delta_auc_std": d_auc.std(ddof=1) if len(folds) > 1 else np.nan,
                     "delta_ece_mean": d_ece.mean(), "worst_slice": worst_slice, "worst_slice_delta_auc": worst,
                     "passes_t047_gate": bool(passed)})
    return pd.DataFrame(rows)


def summarise(runs: pd.DataFrame) -> pd.DataFrame:
    g = runs.groupby(["dataset", "model", "max_len"])
    out = g.agg(folds=("fold", "nunique"), auc_mean=("auc", "mean"), auc_std=("auc", "std"),
                accuracy_mean=("accuracy", "mean"), accuracy_std=("accuracy", "std"),
                ece_mean=("ece", "mean"), ece_std=("ece", "std"), best_epoch_mean=("best_epoch", "mean"),
                train_seconds_mean=("train_seconds", "mean"), parameters=("parameters", "first"))
    return out.reset_index()


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def plan_jobs(mode: str, threads: int) -> list[dict]:
    cfg = MODES[mode]
    jobs = []
    for dataset in ("assist2009", "simulated"):
        dcfg = cfg[dataset]
        if not dcfg:
            continue
        for L in dcfg["lengths"]:
            models = list(dcfg["models"]) + (dcfg["main_only_models"] if L == dcfg["main_length"] else [])
            for model in models:
                for fold in cfg["folds"]:
                    jobs.append({"dataset": dataset, "model": model, "max_len": L, "fold": fold,
                                 "seed": 1000 + fold, "mode": mode, "threads": threads,
                                 "max_epochs": cfg["max_epochs"], "patience": cfg["patience"]})
    # longest jobs first keeps the workers busy until the end
    cost = {"dkt": 1, "sakt": 2, "akt": 4, "saint": 4, "saint_plus": 4, "saint_plus_notime": 4, "saint_plus_fairtime": 4}
    jobs.sort(key=lambda j: -(cost[j["model"]] * j["max_len"] * (3 if j["dataset"] == "assist2009" else 1)))
    return jobs


def write_tables(out_dir: Path, prefix: str, results: list[dict]):
    runs = pd.DataFrame([r["run"] for r in results]).sort_values(["dataset", "model", "max_len", "fold"])
    slices = pd.DataFrame([s for r in results for s in r["slices"]])
    calib = pd.DataFrame([c for r in results for c in r["calibration"]])
    hist = pd.DataFrame([{**{k: r["run"][k] for k in ("dataset", "model", "max_len", "fold")}, **h}
                         for r in results for h in r["history"]])
    runs.to_csv(out_dir / f"{prefix}_runs.csv", index=False, float_format="%.5f")
    if len(slices):
        slices.sort_values(["dataset", "model", "max_len", "fold", "slice"]).to_csv(
            out_dir / f"{prefix}_slices.csv", index=False, float_format="%.5f")
    calib.to_csv(out_dir / f"{prefix}_calibration.csv", index=False, float_format="%.5f")
    hist.to_csv(out_dir / f"{prefix}_history.csv", index=False, float_format="%.5f")
    return runs, slices


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--mode", choices=list(MODES), default="quick")
    ap.add_argument("--workers", type=int, default=min(4, os.cpu_count() or 1),
                    help="parallel training processes (each uses --threads threads)")
    ap.add_argument("--threads", type=int, default=1, help="torch threads per training process")
    ap.add_argument("--mlflow", choices=["auto", "server", "off"], default="auto")
    ap.add_argument("--out", type=Path, default=RESULTS_DIR)
    ap.add_argument("--skip-latency", action="store_true")
    args = ap.parse_args(argv)

    t_start = time.time()
    args.out.mkdir(parents=True, exist_ok=True)
    prefix = f"t040_{args.mode}"
    cfg = MODES[args.mode]
    data_sha = {"assist2009": sha256_file(kb_data.download_assist2009())}
    provenance = {"ticket": "T040", "mode": args.mode, "started": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
                  "config": {k: v for k, v in cfg.items()}, "hyperparameters": HYPER,
                  "fold_seed": FOLD_SEED, "n_folds": N_FOLDS, "data_sha256": data_sha,
                  "data_sources": DATA_SOURCES, "code": code_version(), "environment": environment(),
                  "workers": args.workers, "threads_per_worker": args.threads,
                  "assist2017": "not used: the official source (sites.google.com/view/assistmentsdatamining/dataset) "
                                "gives the file only after an email sign-up and acceptance of terms of use "
                                "(no redistribution, declared purpose, publish code); needs the product owner's decision",
                  "ednet": "not used: no reachable official source and CC BY-NC 4.0 licence"}
    mlflow = mlflow_setup(args.mlflow)
    jobs = plan_jobs(args.mode, args.threads)
    print(f"{len(jobs)} training runs, {args.workers} workers x {args.threads} threads, mode {args.mode}")

    results = []
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        futures = {pool.submit(run_job, j): j for j in jobs}
        for fut in as_completed(futures):
            out = fut.result()
            results.append(out)
            r = out["run"]
            print(f"[{len(results):3d}/{len(jobs)} {time.time() - t_start:6.0f}s] {r['dataset']:10s} {r['model']:19s} "
                  f"L={r['max_len']:3d} fold {r['fold']}  AUC {r['auc']:.4f}  ECE {r['ece']:.4f}  "
                  f"epochs {r['epochs_run']} (best {r['best_epoch']})  {r['job_seconds']:.0f}s", flush=True)
            mlflow_log(mlflow, out, provenance)
            write_tables(args.out, prefix, results)
    train_wall = time.time() - t_start
    runs, slices = write_tables(args.out, prefix, results)

    latency = []
    if not args.skip_latency:
        print("CPU inference latency (no training running)")
        for dataset in ("assist2009",):
            n_items, n_kc = vocab_sizes(dataset, args.mode)
            dcfg = cfg[dataset]
            for L in dcfg["lengths"]:
                for model in dcfg["models"]:
                    for batch, iters in cfg["latency_iters"].items():
                        for threads in sorted({1, min(4, os.cpu_count() or 1)}):
                            m = measure_latency(model, n_items, n_kc, L, batch, threads, iters)
                            latency.append({"dataset": dataset, **m})
                            print(f"  {model:11s} L={L:3d} batch {batch:2d} threads {threads}: "
                                  f"{m['ms_per_call_median']:.2f} ms per call, {m['ms_per_prediction']:.3f} ms per prediction")
                    latency.append({"dataset": dataset, "model": model, "max_len": L, "batch": None, "threads": None,
                                    "device": "gpu", "iters": 0, "ms_per_call_median": None, "ms_per_call_p95": None,
                                    "ms_per_prediction": None, "parameters": None,
                                    "note": "pending: no GPU before the cloud (S8+)"})
        pd.DataFrame(latency).to_csv(args.out / f"{prefix}_latency.csv", index=False, float_format="%.4f")

    summary = summarise(runs)
    summary.to_csv(args.out / f"{prefix}_summary.csv", index=False, float_format="%.5f")
    gates = []
    for dataset in ("assist2009", "simulated"):
        dcfg = cfg[dataset]
        if dcfg:
            for L in dcfg["lengths"]:
                gates.append(gate_vs_baseline(runs, slices, dataset, L))
    gates = pd.concat(gates) if gates else pd.DataFrame()
    gates.to_csv(args.out / f"{prefix}_gate.csv", index=False, float_format="%.5f")
    provenance.update({"finished": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
                       "training_wall_seconds": round(train_wall, 1),
                       "total_wall_seconds": round(time.time() - t_start, 1), "training_runs": len(results)})
    (args.out / f"{prefix}_meta.json").write_text(json.dumps(provenance, indent=2, default=str))

    pd.set_option("display.width", 200)
    if args.mode == "quick":
        print("\nQUICK MODE: a smoke test on a small sample with 2 epochs. Do not compare models on these numbers.")
    print("\nAUC / ECE (mean and standard deviation over folds)")
    print(summary[["dataset", "model", "max_len", "folds", "auc_mean", "auc_std", "ece_mean", "ece_std",
                   "accuracy_mean"]].round(4).to_string(index=False))
    if len(gates):
        print("\nT047 gate against DKT (fold-paired)")
        print(gates.round(4).to_string(index=False))
    print(f"\nDone in {time.time() - t_start:.0f} s; results in {args.out}")


if __name__ == "__main__":
    main()
