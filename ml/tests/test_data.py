"""What the brain sees (kuizi_brain/data.py): the student simulator, the split by student and the
ASSISTments loader, tested on synthetic files so nothing is downloaded."""

import numpy as np
import pandas as pd
import pytest

from kuizi_brain import data as D
from kuizi_brain import graph as G

N_STUDENTS, ANSWERS = 40, 30


@pytest.fixture(scope="module")
def sim():
    return D.simulate_students(n_students=N_STUDENTS, answers_per_student=ANSWERS, seed=3)


def test_simulation_has_one_row_per_answer_with_observed_and_hidden_columns(sim):
    assert len(sim) == N_STUDENTS * ANSWERS
    observed = ["student", "t", "item", "kc", "kc_name", "correct", "elapsed_s", "lag_s", "hints"]
    hidden = ["p_true", "mastery_true"]
    assert set(observed + hidden + ["time_multiplier", "assistive"]) <= set(sim.columns)
    assert set(sim.correct.unique()) <= {0, 1}
    assert sim.hints.between(0, 2).all()
    assert (sim.elapsed_s > 0).all() and (sim.lag_s > 0).all()
    assert sim.p_true.between(0.15, 1 - 0.08).all()  # squeezed between guess and slip
    assert sim.groupby("student").t.apply(lambda t: t.is_monotonic_increasing).all()


def test_simulation_describes_its_item_bank(sim):
    n_kc = len(G.PHYSICS_KCS)
    assert sim.attrs["n_kc"] == n_kc
    assert sim.attrs["n_items"] == n_kc * 25
    assert (sim.attrs["item_kc"][sim.item] == sim.kc).all()
    assert sim.attrs["final_p_true"].shape == (N_STUDENTS, n_kc)
    assert set(sim.kc_name) <= {french for french, _, _ in G.PHYSICS_KCS.values()}


def test_simulation_is_reproducible():
    a = D.simulate_students(n_students=5, answers_per_student=10, seed=11)
    b = D.simulate_students(n_students=5, answers_per_student=10, seed=11)
    c = D.simulate_students(n_students=5, answers_per_student=10, seed=12)
    pd.testing.assert_frame_equal(a, b)
    assert not a.correct.equals(c.correct) or not a.item.equals(c.item)


def test_accommodations_are_per_student_and_assistive_mode_implies_extra_time(sim):
    per_student = sim.groupby("student")[["time_multiplier", "assistive"]].nunique()
    assert (per_student == 1).all().all()
    assert set(sim.time_multiplier.unique()) <= {1.0, 1.33, 1.5}
    assert (sim[sim.assistive].time_multiplier > 1).all()


def test_no_accommodation_when_the_share_is_zero():
    df = D.simulate_students(n_students=10, answers_per_student=5, seed=1, share_with_accommodation=0.0)
    assert (df.time_multiplier == 1.0).all()
    assert not df.assistive.any()


def test_split_by_student_never_shares_a_student(sim):
    train, test = D.split_by_student(sim, test_share=0.25, seed=1)
    assert not set(train.student) & set(test.student)
    assert len(train) + len(test) == len(sim)
    assert test.student.nunique() == N_STUDENTS // 4
    again_train, _ = D.split_by_student(sim, test_share=0.25, seed=1)
    pd.testing.assert_frame_equal(train, again_train)


def test_download_rejects_a_file_with_the_wrong_fingerprint(tmp_path):
    (tmp_path / D.ASSIST2009_FILE).write_text("not the ASSISTments file")
    with pytest.raises(ValueError, match="does not match"):
        D.download_assist2009(tmp_path)


def _assist_rows(user, n, original=1, skill=7.0, start=0):
    return [
        {
            "user_id": user,
            "order_id": start + n - i,  # written newest first: the loader must sort
            "problem_id": 100 + i,
            "skill_id": skill,
            "skill_name": "Equation Solving",
            "correct": i % 2,
            "ms_first_response": 12_000,
            "hint_count": 0,
            "original": original,
        }
        for i in range(n)
    ]


def test_assist2009_loader_keeps_first_attempts_and_active_students(tmp_path, monkeypatch):
    rows = (
        _assist_rows(user=501, n=6)
        + _assist_rows(user=501, n=1, original=0, start=50)  # a scaffolding question: dropped
        + _assist_rows(user=501, n=1, skill=np.nan, start=60)  # no skill: dropped
        + _assist_rows(user=502, n=3)  # fewer than 5 answers: dropped
        + _assist_rows(user=503, n=5)
    )
    rows[0]["ms_first_response"] = -50  # negative times are clipped to 0
    rows[1]["ms_first_response"] = 10_000_000  # very long times are capped at 600 s
    path = tmp_path / D.ASSIST2009_FILE
    pd.DataFrame(rows).to_csv(path, index=False, encoding="latin-1")
    monkeypatch.setattr(D, "download_assist2009", lambda data_dir: path)

    df = D.load_assist2009(tmp_path)

    assert list(df.columns) == ["student", "item", "kc", "kc_name", "correct", "elapsed_s", "hints"]
    assert df.groupby("student").size().to_dict() == {0: 6, 1: 5}
    assert df.kc.unique().tolist() == [0]
    assert df.elapsed_s.between(0, 600).all()
    assert df.elapsed_s.min() == 0 and df.elapsed_s.max() == 600
    first_student = df[df.student == 0]
    assert first_student.item.is_monotonic_decreasing  # sorted by order_id, oldest answer first
