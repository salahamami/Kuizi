"""What the brain sees: answer sequences (T023, T024, T219).

Two sources, both safe to use on a PC:
- ASSISTments 2009 skill-builder data: real answers from 4,217 US middle-school students on
  maths skills. Public research data; cite Feng, Heffernan & Koedinger (2009). Used here to
  learn and to benchmark only (T040). Kuizi's production models train on Kuizi data (T239).
- A simulator of Bac Physics students on the concept graph in graph.py. Every simulated
  student has a known true mastery, so a notebook can check whether a model finds it, and the
  simulator produces the time features (elapsed time, lag time) that SAINT+ uses.
No real Kuizi student data is ever used here.
"""

import hashlib
import urllib.request
from pathlib import Path

import numpy as np
import pandas as pd

from . import graph as G

DATA_DIR = Path(__file__).resolve().parent.parent / "data"

ASSIST2009_URL = "https://drive.google.com/uc?export=download&id=1NNXHFRxcArrU0ZJSb9BIL56vmUt5FhlE"
ASSIST2009_FILE = "skill_builder_data_corrected_collapsed.csv"
ASSIST2009_SHA256 = "162ef8d2d28bcbfea6591a282994062bd8d5eaa00636544292a0d268dca6e5da"


def download_assist2009(data_dir=DATA_DIR):
    """Download ASSISTments 2009 (64 MB) once into ml/data/ and check its fingerprint."""
    path = Path(data_dir) / ASSIST2009_FILE
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        tmp = path.with_suffix(".part")
        urllib.request.urlretrieve(ASSIST2009_URL, tmp)
        tmp.rename(path)
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    if digest != ASSIST2009_SHA256:
        raise ValueError(f"{path} does not match the expected file; delete it and download again")
    return path


def load_assist2009(data_dir=DATA_DIR, min_answers=5):
    """ASSISTments 2009 as one row per answer, in the order each student answered.

    Keeps first attempts at main problems (original == 1), drops rows without a skill and
    students with fewer than `min_answers` answers. Columns: student, item, kc (integer ids
    starting at 0), kc_name, correct (0/1), elapsed_s (time to first response), hints.
    This dataset has no timestamps, so there is no lag time here; the simulator has one.
    """
    path = download_assist2009(data_dir)
    raw = pd.read_csv(path, low_memory=False, encoding="latin-1")
    df = raw[(raw.original == 1) & raw.skill_id.notna()].copy()
    df = df.sort_values(["user_id", "order_id"])
    df = df[df.groupby("user_id").user_id.transform("size") >= min_answers]
    out = pd.DataFrame({
        "student": df.user_id.astype("category").cat.codes.astype("int64"),
        "item": df.problem_id.astype("category").cat.codes.astype("int64"),
        "kc": df.skill_id.astype(str).astype("category").cat.codes.astype("int64"),
        "kc_name": df.skill_name.astype(str),
        "correct": df.correct.astype(int),
        "elapsed_s": (df.ms_first_response.clip(lower=0) / 1000).clip(upper=600),
        "hints": df.hint_count.astype(int),
    })
    return out.reset_index(drop=True)


def simulate_students(n_students=600, answers_per_student=120, items_per_kc=25, seed=7,
                      share_with_accommodation=0.15, kc_graph=G.PHYSICS_KCS):
    """Simulated Bac Physics students on the concept graph (T219 builds the production version).

    Each student has a general ability and a hidden mastery per concept (a logit). A concept
    starts lower when its prerequisites are weak. Practising a concept raises its mastery
    (learning) and long gaps lower it (forgetting). The chance of a correct answer is
    sigmoid(mastery + ability - item difficulty), squeezed between a guess and a slip rate.

    Some students have an official accommodation: a time multiplier (x1.33 or x1.5) and
    sometimes a screen reader (assistive mode). They take longer to answer but know just as
    much, which is exactly what a fair model must not confuse with weakness (T148).

    Returns one row per answer with the observed columns (student, t, item, kc, kc_name,
    correct, elapsed_s, lag_s, hints, time_multiplier, assistive) and the hidden truth
    (p_true: the real chance of success at that moment, mastery_true: the concept's mastery
    as a probability, for a typical item). `df.attrs` holds the item bank (item_kc,
    item_difficulty) and final_p_true, each student's true chance of success on a typical item
    of every concept at the end.
    """
    rng = np.random.default_rng(seed)
    kcs = G.topological_order(kc_graph)
    k_index = {kc: i for i, kc in enumerate(kcs)}
    n_kc = len(kcs)
    item_kc = np.repeat(np.arange(n_kc), items_per_kc)
    item_b = rng.normal(0.0, 0.8, size=len(item_kc))
    guess, slip = 0.15, 0.08
    rows = []
    final_p = np.zeros((n_students, n_kc))
    for s in range(n_students):
        ability = rng.normal(0, 0.7)
        mastery = np.zeros(n_kc)
        for kc in kcs:
            pre = [k_index[p] for p in kc_graph[kc][2]]
            base = rng.normal(-0.8, 0.9)
            if pre:
                base += 0.5 * np.mean(mastery[pre])
            mastery[k_index[kc]] = base
        learn_rate = rng.uniform(0.08, 0.3)
        has_acc = rng.random() < share_with_accommodation
        multiplier = rng.choice([1.33, 1.5]) if has_acc else 1.0
        assistive = bool(has_acc and rng.random() < 0.4)
        speed = rng.lognormal(0, 0.25)
        # The student's route: walks the concepts roughly in programme order, with revisits.
        frontier = 0
        t = 0.0
        last_seen = np.full(n_kc, -np.inf)
        for _ in range(answers_per_student):
            if rng.random() < 0.7:
                k = min(frontier + rng.integers(0, 2), n_kc - 1)
            else:
                k = rng.integers(0, frontier + 1)
            item = rng.choice(np.flatnonzero(item_kc == k))
            gap = rng.exponential(90) if rng.random() < 0.85 else rng.exponential(3 * 86400)
            t += gap
            if np.isfinite(last_seen[k]):
                days = (t - last_seen[k]) / 86400
                mastery[k] -= 0.15 * (1 - np.exp(-days / 7))
            logit = mastery[k] + ability - item_b[item]
            p = guess + (1 - guess - slip) / (1 + np.exp(-logit))
            correct = int(rng.random() < p)
            uncertainty = 1 - abs(2 * p - 1)
            elapsed = rng.lognormal(np.log(35 + 50 * uncertainty), 0.35) * speed * multiplier
            hints = int(rng.random() < 0.6 * (1 - p)) + int(rng.random() < 0.25 * (1 - p))
            rows.append((s, t, item, k, kcs[k], correct, elapsed, gap, hints, multiplier, assistive,
                         p, 1 / (1 + np.exp(-(mastery[k] + ability)))))
            mastery[k] += learn_rate * (1.0 if correct else 0.6)
            last_seen[k] = t
            if mastery[k] + ability > 0.8 and frontier == k:
                frontier = min(frontier + 1, n_kc - 1)
        final_p[s] = guess + (1 - guess - slip) / (1 + np.exp(-(mastery + ability)))
    df = pd.DataFrame(rows, columns=["student", "t", "item", "kc", "kc_id", "correct", "elapsed_s",
                                     "lag_s", "hints", "time_multiplier", "assistive", "p_true",
                                     "mastery_true"])
    df["kc_name"] = df.kc_id.map(lambda k: kc_graph[k][0])
    df.attrs["n_items"] = len(item_kc)
    df.attrs["n_kc"] = n_kc
    df.attrs["item_kc"] = item_kc
    df.attrs["item_difficulty"] = item_b
    df.attrs["final_p_true"] = final_p   # true chance of success on a typical item (difficulty 0), per student and concept, at the end
    return df


def split_by_student(df, test_share=0.2, seed=0):
    """Train/test split by student, never by row: the test students are people the model has
    never seen, as in production. Splitting rows would leak a student's future into training."""
    rng = np.random.default_rng(seed)
    students = df.student.unique()
    test = set(rng.choice(students, size=int(len(students) * test_share), replace=False))
    is_test = df.student.isin(test)
    return df[~is_test].reset_index(drop=True), df[is_test].reset_index(drop=True)
