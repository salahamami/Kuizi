"""How the brain is judged (kuizi_brain/metrics.py): AUC, accuracy, calibration."""

import matplotlib.pyplot as plt
import pytest

from kuizi_brain import metrics as M


def test_auc_ranks_right_answers_above_wrong_ones():
    y = [0, 0, 1, 1]
    assert M.auc(y, [0.1, 0.2, 0.8, 0.9]) == 1.0
    assert M.auc(y, [0.9, 0.8, 0.2, 0.1]) == 0.0
    assert M.auc(y, [0.5, 0.5, 0.5, 0.5]) == 0.5


def test_accuracy_uses_the_threshold():
    y, p = [0, 1, 1, 0], [0.4, 0.6, 0.5, 0.7]
    assert M.accuracy(y, p) == 0.75  # 0.5 counts as "right"
    assert M.accuracy(y, p, threshold=0.65) == 0.25


def test_calibration_table_groups_predictions_in_equal_bins():
    y = [0, 1, 0, 1, 1, 1]
    p = [0.05, 0.05, 0.55, 0.55, 0.95, 1.0]  # 1.0 belongs to the last bin
    table = M.calibration_table(y, p)
    assert list(table.bin) == ["0.0-0.1", "0.5-0.6", "0.9-1.0"]
    assert list(table.answers) == [2, 2, 2]
    assert list(table.observed) == [0.5, 0.5, 1.0]
    assert table.predicted.iloc[2] == pytest.approx(0.975)


def test_expected_calibration_error_is_zero_when_predictions_match_reality():
    p = [0.25] * 4 + [0.75] * 4
    y = [1, 0, 0, 0, 1, 1, 1, 0]  # 1 right in 4 at 25 %, 3 right in 4 at 75 %
    assert M.expected_calibration_error(y, p) == pytest.approx(0.0)


def test_expected_calibration_error_measures_overconfidence():
    assert M.expected_calibration_error([1, 0] * 5, [0.9] * 10) == pytest.approx(0.4)


def test_report_rounds_every_metric_and_counts_answers():
    y, p = [0, 1, 1, 0, 1], [0.2, 0.7, 0.6, 0.4, 0.9]
    # every prediction sits alone in its bin: gaps 0.2, 0.4, 0.4, 0.3, 0.1, mean 0.28
    assert M.report("demo", y, p) == {"model": "demo", "AUC": 1.0, "accuracy": 1.0, "ECE": 0.28, "answers": 5}


def test_reliability_diagram_uses_a_marker_and_a_label_not_only_colour():
    _, ax = plt.subplots()
    M.plot_reliability(ax, [0, 1, 1, 0, 1, 1], [0.1, 0.8, 0.7, 0.3, 0.9, 0.6], "model A", marker="s")
    diagonal, model = ax.lines
    assert diagonal.get_linestyle() == ":"
    assert model.get_marker() == "s"
    assert [t.get_text() for t in ax.get_legend().get_texts()] == ["model A"]
    assert ax.get_xlim() == (0, 1) and ax.get_ylim() == (0, 1)
