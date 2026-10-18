# Knowledge-tracing benchmark (T040)

Compares five knowledge-tracing models on public and simulated data and feeds the production-model decision in [ADR 0007](../../docs/architecture/decisions/0007-knowledge-tracing-model.md) (Proposed). Ticket T040 (KK-60).

| File | What it is |
| --- | --- |
| `kt_benchmark.py` | The benchmark: data, split by student, training, evaluation, slices, CPU latency, MLflow logging |
| `t040_benchmark.ipynb` | Reads the saved results and shows the tables and charts (trains nothing, runs in seconds) |
| `check_kt_benchmark.py` | Self-checks on synthetic data (seconds): every test answer predicted once, every model causal and independent of padding and batch size, Platt keeps the AUC, the gate thresholds |
| `results/t040_full_*` | The full run reported in ADR 0007: one row per training run (`runs`), slice, calibration bin, epoch (`history`) and latency measurement, plus the summary, the T047 gate table and `meta.json` (environment, data fingerprint, code version, timings) |
| `results/t040_full_assist2009-L100_*` | Second run, ASSISTments 2009 at windows of 100, with Platt calibration (`ece_platt`, gate after calibration); its AUCs equal the full run's in all 18 runs |

## How to run

```bash
make ml-setup                                         # once: Python 3.12, PyTorch (CPU), pyKT, JupyterLab
cd ml
uv run python benchmarks/check_kt_benchmark.py       # fairness checks of the benchmark itself: seconds
uv run python benchmarks/kt_benchmark.py --mode quick # smoke test: under 1 minute on 4 cores
uv run python benchmarks/kt_benchmark.py --mode full  # everything: 38 minutes on 4 cores (69 training runs + latency)
uv run python benchmarks/kt_benchmark.py --mode full --datasets assist2009 --lengths 100 --skip-latency
                                                      # the calibration run: 11 minutes (18 training runs)
make ml-lab                                           # then open benchmarks/t040_benchmark.ipynb
```

The first run downloads ASSISTments 2009 (64 MB) into `ml/data/` and checks its fingerprint. Quick mode trains every model for 2 epochs on 600 students: it only checks that the code runs, and its numbers must not be used to compare models (its result files are git-ignored).

Options: `--workers` (parallel training processes, default 4), `--threads` (PyTorch threads per process, default 1: on small models four single-thread processes are faster than one four-thread process), `--datasets` and `--lengths` (run part of a mode; the result files get a suffix such as `_assist2009-L100`, or `--tag`), `--mlflow auto|server|off`, `--skip-latency`, `--out`.

**Which code produced which files.** Platt calibration and the `--datasets` / `--lengths` options were added after the full run, so `t040_full_*` has no `ece_platt` column and its `meta.json` records the earlier code hash. The training path did not change: the calibration run, made with the current script, reproduced every AUC of the full run at windows of 100 exactly. Running the current script in full mode gives the same numbers plus the calibration columns. Training is deterministic for a given seed on the same machine and library versions.

## What the full mode runs

| Dataset | Models | Window lengths | Folds |
| --- | --- | --- | --- |
| ASSISTments 2009 | DKT, SAKT, SAINT, AKT, SAINT+ | 50, 100, 200 | 3 |
| ASSISTments 2009 | SAINT+ without time features (ablation) | 100 | 3 |
| Simulated Bac Physics students | DKT, SAKT, SAINT, AKT, SAINT+, SAINT+ without time, SAINT+ with time divided by the multiplier | 100 | 3 |

Then CPU inference latency for the five models at every window length, batch 1 and 64, one and four threads.

## Protocol

- **Split by student, never by answer.** Students are assigned to 5 folds with a fixed seed (2026); a run tests on one fold and trains on the others, holding out 10 % of the training students for early stopping. Three folds are run, so every number is a mean ± standard deviation over three disjoint groups of test students.
- **Same windows and same predictions for every model.** Training uses non-overlapping windows of `max_len` answers. Validation and test use windows that overlap by half: every answer of a test student except the first is predicted exactly once, from at least half a window of earlier answers when the student has them, as the online sequence builder (T048) will do.
- **Same budget for every model.** Width 64, 4 attention heads, dropout 0.2, Adam (learning rate 0.001), batch 64, gradient clipping 1.0, up to 20 epochs with early stopping on validation AUC (patience 3). No model was tuned individually; T041 and T042 tune the chosen one.
- **Batches of similar length, every answer weighted the same.** Most students have short histories (median 24 answers), so random batches are almost always padded to the full window and waste up to two thirds of the compute. Training batches are therefore grouped by length (like Hugging Face's `group_by_length`), and the loss is summed over the batch and divided by the average number of answers per batch, so every answer weighs as much as with random batches. A plain per-batch mean is not neutral: in a check on fold 0 with windows of 200, it lowered AKT's AUC from 0.772 to 0.754, while the weighted loss gave 0.768 for AKT and 0.6994 for SAINT (0.6994 with random batches).
- **Metrics.** AUC, accuracy (threshold 0.5), ECE (10 equal-width bins), and per slice: position in the student's history (answers 2–10, 11–50, 51+) and, on the simulator, accommodation groups (no accommodation, extra time ×1.33 or ×1.5, assistive mode).
- **T047 gate rule.** A challenger is called better than DKT only if, paired by fold, its AUC is at least 0.005 higher, no slice loses more than 0.01 AUC, and ECE is not worse by more than 0.01 (`results/t040_full_gate.csv`). The gate is computed on raw ECE and, where available, after Platt calibration of both models (`ece_metric` column).
- **Calibration.** After training, Platt scaling (P' = sigmoid(a · logit P + b), two numbers per model) is fitted on the validation students and applied to the test students. AUC does not change; `ece_platt` and `accuracy_platt` report the calibrated predictions.
- **Latency.** One forward pass over a full window predicts the next answer of every student in the batch; reported as the median ms per prediction (and p95 per call) with freshly initialised weights (compute time does not depend on their values). **GPU latency is pending**: there is no GPU before the cloud (S8+).
- **Implementations.** DKT, SAKT, SAINT and AKT come from pyKT (`pykt-toolkit` 0.0.38, the version in `uv.lock`). pyKT has no SAINT+ (its `saint_plus_plus.py` is a different model), so SAINT+ is `kuizi_brain.models.SaintPlus` from T238. Every model was checked to be causal: changing the answer or time at step t never changes a prediction up to t.

## MLflow

Every training run is logged to the experiment `t040-kt-benchmark` with its parameters, seed, fold, data source and fingerprint, code version (git commit, uncommitted-changes flag and a hash of the benchmark and `kuizi_brain` code), library versions, metrics, slices and per-epoch curves. The script uses `MLFLOW_TRACKING_URI` (environment or `.env`) when the local server from `make up` answers, so start `make up` first to see the runs in the MLflow UI. Otherwise it logs to a file store in `benchmarks/mlruns/` (git-ignored); the `mlflow-skinny` client in `ml/` has no UI server, so that store is a record to import or inspect, not something to browse. `--mlflow server` refuses to run without a reachable server.

## Data and licences

- **ASSISTments 2009–2010 skill builder** (corrected, collapsed; 258,153 first-attempt answers from 3,628 students on 15,901 problems and 145 skill tags after the T238 loader's filters). Public research data, linked openly from the [official page](https://sites.google.com/site/assistmentsdata/home/2009-2010-assistment-data/skill-builder-data-2009-2010), which asks users to cite that URL and Feng, M., Heffernan, N. T., & Koedinger, K. R. (2009), *Addressing the assessment challenge with an online system that tutors as it assesses*, User Modeling and User-Adapted Interaction 19(3). It has elapsed time but no timestamps, so there is no lag time.
- **ASSISTments 2017** (data mining competition) is **not used**. The [official source](https://sites.google.com/view/assistmentsdatamining/dataset) sends the file only after an email sign-up and acceptance of the ASSISTments terms of use (no sharing of the data, use only for the stated purpose, publish the code of any paper). Signing up and accepting those terms is the product owner's decision.
- **EdNet** is not used: no official source was reachable and its licence (CC BY-NC 4.0) does not allow commercial use.
- **Simulated students** come from `kuizi_brain.data.simulate_students` (600 students × 120 answers, seed 7); no real person is behind them. They provide lag time and accommodations, which no public dataset has.
- Data files live in `ml/data/` (git-ignored) and are never committed. Real Kuizi student data never goes on a PC: the re-run on pilot data (T239) runs in the cloud environment, with `load_dataset` replaced by the pilot adapter from T041.
