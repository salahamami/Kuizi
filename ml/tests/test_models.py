"""The brain's models (kuizi_brain/models.py): batches, IRT and the cold start, and the shared
contract of every sequence model (BKT, DKT, SAINT+): one logit per position, using only the past.
Models are tiny and trained for a few steps, so these tests check behaviour, not accuracy."""

import numpy as np
import pandas as pd
import pytest
import torch

from kuizi_brain import data as D
from kuizi_brain import models as M

N_KC = 12  # concepts in the Physics graph


@pytest.fixture(scope="module")
def sim():
    return D.simulate_students(n_students=24, answers_per_student=30, seed=5)


def answers(lengths, multiplier=1.0):
    rows = [(s, i, i % 3, i % 2, 20.0 * multiplier, 60.0, multiplier) for s, n in enumerate(lengths) for i in range(n)]
    return pd.DataFrame(rows, columns=["student", "item", "kc", "correct", "elapsed_s", "lag_s", "time_multiplier"])


def random_batch(n_items=30, n_kc=N_KC, size=2, length=12, seed=0):
    g = torch.Generator().manual_seed(seed)
    return {
        "item": torch.randint(1, n_items + 1, (size, length), generator=g),
        "kc": torch.randint(1, n_kc + 1, (size, length), generator=g),
        "correct": torch.randint(0, 2, (size, length), generator=g),
        "elapsed": torch.rand(size, length, generator=g),
        "lag": torch.rand(size, length, generator=g),
        "mask": torch.ones(size, length, dtype=torch.bool),
    }


SEQUENCE_MODELS = {
    "bkt": lambda: M.BKT(N_KC),
    "dkt": lambda: M.DKT(N_KC, hidden=16),
    "saint_plus": lambda: M.SaintPlus(30, N_KC, d=16, heads=2, layers=1, max_len=12, dropout=0.0),
    "saint_plus_notime": lambda: M.SaintPlus(30, N_KC, d=16, heads=2, layers=1, max_len=12, use_time=False),
}


# --- batches ---------------------------------------------------------------------------------


def test_windows_cut_each_student_and_pad_with_zero():
    W = M.make_windows(answers([5, 3]), max_len=4)
    assert W["mask"].shape == (3, 4)  # student 0: 4 + 1 answers, student 1: 3 answers
    assert W["mask"].sum().item() == 8
    assert W["student"][:, 0].tolist() == [0, 0, 1]
    assert (W["item"][~W["mask"]] == 0).all()
    assert W["item"][0].tolist() == [1, 2, 3, 4]  # ids shifted by one: 0 means padding
    assert W["item"].dtype == torch.long and W["elapsed"].dtype == torch.float32


def test_fair_time_removes_the_official_time_multiplier():
    """T148: a student with x1.5 extra time who takes 30 s looks like a student who takes 20 s."""
    regular = M.make_windows(answers([4]), max_len=4, time_multiplier_fairness=True)
    extra_time = M.make_windows(answers([4], multiplier=1.5), max_len=4, time_multiplier_fairness=True)
    unfair = M.make_windows(answers([4], multiplier=1.5), max_len=4)
    assert torch.allclose(regular["elapsed"], extra_time["elapsed"])
    assert not torch.allclose(regular["elapsed"], unfair["elapsed"])


def test_windows_without_lag_time_use_zero():
    W = M.make_windows(answers([3]).drop(columns="lag_s"), max_len=3)
    assert (W["lag"] == 0).all()


# --- IRT and the cold start ------------------------------------------------------------------


def test_irt_recovers_the_order_of_item_difficulties():
    rng = np.random.default_rng(0)
    true_b = np.array([-1.5, -0.5, 0.0, 0.5, 1.5])
    n_students = 300
    theta = rng.normal(0, 1, n_students)
    student = np.repeat(np.arange(n_students), len(true_b))
    item = np.tile(np.arange(len(true_b)), n_students)
    correct = (rng.random(len(item)) < 1 / (1 + np.exp(-(theta[student] - true_b[item])))).astype(int)
    model = M.IRT(n_students, len(true_b))
    model.fit(student, item, correct, epochs=200)
    b, a = model.item_params()
    assert np.argsort(b).tolist() == np.argsort(true_b).tolist()
    assert (a > 0).all()


def test_cold_start_ability_moves_with_answers_and_gets_surer():
    b, a = np.zeros(5), np.ones(5)
    prior_mean, prior_sd = M.estimate_ability([], [], b, a)
    right, right_sd = M.estimate_ability(range(5), [1] * 5, b, a)
    wrong, _ = M.estimate_ability(range(5), [0] * 5, b, a)
    assert prior_mean == pytest.approx(0.0, abs=1e-9)
    assert prior_sd == pytest.approx(1.0, abs=0.01)
    assert right > 0 > wrong
    assert right == pytest.approx(-wrong)
    assert right_sd < prior_sd


def test_cold_start_rejects_answers_that_do_not_match_the_items():
    with pytest.raises(ValueError):
        M.estimate_ability([0, 1], [1], np.zeros(2), np.ones(2))


def test_item_information_peaks_at_the_item_difficulty():
    theta = np.linspace(-3, 3, 601)
    info = M.item_information(theta, b=0.5, a=1.2)
    assert theta[info.argmax()] == pytest.approx(0.5)
    assert info.max() == pytest.approx(1.2**2 / 4)


# --- sequence models -------------------------------------------------------------------------


@pytest.mark.parametrize("name", SEQUENCE_MODELS)
def test_sequence_models_give_one_logit_per_position_from_the_past_only(name):
    torch.manual_seed(0)
    model = SEQUENCE_MODELS[name]().eval()
    batch = random_batch()
    t = 6
    batch["kc"][:, t + 1] = batch["kc"][:, t]  # BKT tracks each concept on its own: practise it again
    changed = {k: v.clone() for k, v in batch.items()}
    changed["correct"][:, t] = 1 - changed["correct"][:, t]
    changed["elapsed"][:, t] = 0.9
    with torch.no_grad():
        before, after = model(batch), model(changed)
    assert before.shape == (2, 12)
    assert torch.allclose(before[:, : t + 1], after[:, : t + 1], atol=1e-6), "a model saw the answer it predicts"
    assert not torch.allclose(before[:, t + 1 :], after[:, t + 1 :], atol=1e-6), "a model ignores past answers"


def test_bkt_parameters_are_probabilities_with_bounded_guess_and_slip():
    init, learn, guess, slip = M.BKT(N_KC).params()
    for p in (init, learn):
        assert ((p > 0) & (p < 1)).all()
    for p in (guess, slip):
        assert ((p > 0) & (p < 0.5)).all()


def test_dkt_sees_every_concept_at_every_step():
    model = M.DKT(N_KC, hidden=16)
    p = model.predict_all(random_batch())
    assert p.shape == (2, 12, N_KC)
    assert ((p > 0) & (p < 1)).all()


def test_training_lowers_the_loss_and_prediction_returns_probabilities(sim):
    W = M.make_windows(sim, max_len=15)
    model = M.DKT(N_KC, hidden=16)
    history = M.fit(model, W, epochs=4, batch_size=16, lr=1e-2, verbose=False)
    assert len(history) == 4
    assert history[-1] < history[0]
    y, p = M.predict(model, W)
    assert len(y) == len(p) == W["mask"].sum().item() == len(sim)
    assert ((p > 0) & (p < 1)).all()


def test_mastery_probe_gives_one_probability_and_one_attention_map_per_concept(sim):
    model = M.SaintPlus(sim.attrs["n_items"], N_KC, d=16, heads=2, layers=1, max_len=12)
    history = sim[sim.student == 0]
    mastery, attention = M.probe_mastery(model, history, sim.attrs["item_kc"], sim.attrs["item_difficulty"], max_len=12)
    assert set(mastery) == set(range(N_KC))
    assert all(0 < p < 1 for p in mastery.values())
    assert attention[0].shape == (11,)  # the last max_len - 1 answers of the history
    # weights over the history; the rest of the attention stays on the probed item itself
    assert (attention[0] >= 0).all() and attention[0].sum() <= 1 + 1e-6


def test_typical_item_is_the_one_closest_to_average_difficulty():
    item_kc = [0, 0, 0, 1, 1]
    difficulty = [1.2, -0.1, 0.4, -2.0, 0.3]
    assert M.typical_items(item_kc, difficulty) == {0: 1, 1: 4}


def test_causal_mask_forbids_looking_ahead():
    assert M.causal_mask(3).tolist() == [[False, True, True], [False, False, True], [False, False, False]]


def test_count_parameters_counts_trainable_weights_only():
    model = M.BKT(N_KC)
    assert M.count_parameters(model) == (N_KC + 1) * 4
    model.logits.requires_grad_(False)
    assert M.count_parameters(model) == 0
