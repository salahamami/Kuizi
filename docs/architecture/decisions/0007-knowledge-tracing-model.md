# 0007. Knowledge-tracing model for the brain

- Status: Proposed (the product owner decides)
- Date: 2026-10-18
- Ticket: T040 (KK-60), proposed by the ML Engineering agent
- Evidence: [`ml/benchmarks/`](../../../ml/benchmarks/README.md): script, results files and the notebook `t040_benchmark.ipynb`

## Context

The backlog assumes the brain is SAINT+ (E05: "self-hosted SAINT+ model", T042 "production SAINT+ model with elapsed-time and lag-time embeddings", TorchServe SAINT+ in the [architecture overview](../overview.md), targets AUC ≥ 0.80 and p99 ≤ 50 ms). The brain walkthrough (T238) found DKT ahead of SAINT+ on ASSISTments 2009, so T040 benchmarks the candidates before T041 and T042 build one.

**What was measured.** DKT (baseline), SAKT, SAINT and AKT from pyKT (`pykt-toolkit` 0.0.38), and SAINT+ from `kuizi_brain` (pyKT has no SAINT+). Every model got the same width (64), optimiser, windows, early stopping and test predictions; none was tuned individually. Students were split into 5 folds by student with a fixed seed. Three folds were run, so each number below is a mean ± standard deviation over three groups of 726 students the model never saw, about 51,400 test answers per fold. Differences are paired by fold. Window lengths were 50, 100 and 200 answers. The T047 gate rule (+0.005 AUC, no slice down more than 0.01 AUC, ECE not worse by more than 0.01) decides whether a model is called better than DKT. The full run took 38 minutes on a 4-core CPU; a second run of 11 minutes added Platt calibration at windows of 100 and reproduced all 18 AUCs exactly.

**Data.** The only real dataset is ASSISTments 2009 (258,153 answers from 3,628 students; 15,901 problems; 145 skill tags; elapsed time but no timestamps). ASSISTments 2017 was not used because its official source releases the file only after an email sign-up and acceptance of terms of use. EdNet was excluded (no reachable official source, CC BY-NC licence). Simulated Bac Physics students (600, from `kuizi_brain`) add lag time and accommodations, which no public dataset has.

## Results

ASSISTments 2009, windows of 100 answers:

| Model | AUC | ECE raw | ECE after Platt | Accuracy | Parameters | CPU ms per request (batch 1, 1 thread) |
| --- | --- | --- | --- | --- | --- | --- |
| **AKT** (pyKT) | **0.7677 ± 0.0027** | 0.0403 ± 0.0177 | 0.0097 ± 0.0089 | 0.7397 | 388,652 | 3.77 |
| DKT (pyKT) | 0.7555 ± 0.0017 | **0.0051 ± 0.0006** | 0.0085 ± 0.0050 | 0.7341 | 61,458 | **0.36** |
| SAKT (pyKT) | 0.7186 ± 0.0036 | 0.0346 ± 0.0127 | 0.0134 ± 0.0032 | 0.7100 | 84,929 | 0.89 |
| SAINT (pyKT) | 0.6991 ± 0.0012 | 0.0336 ± 0.0274 | 0.0062 ± 0.0037 | 0.7082 | 2,195,393 | 2.57 |
| SAINT+ (kuizi_brain) | 0.6987 ± 0.0008 | 0.0294 ± 0.0138 | 0.0109 ± 0.0054 | 0.7098 | 1,267,585 | 3.02 |
| SAINT+ without time | 0.6979 ± 0.0008 | 0.0305 ± 0.0150 | 0.0107 ± 0.0054 | 0.7074 | 1,267,585 | — |

1. **AKT has the best AUC at every window length**: +0.0149 ± 0.0039 over DKT with windows of 50, +0.0122 ± 0.0040 with 100, +0.0132 ± 0.0048 with 200. Its lead grows with history: +0.002 on answers 2–10, +0.011 on answers 11–50, +0.015 on answers 51 and later. No slice is below DKT.
2. **SAINT and SAINT+ are about 0.057 AUC below DKT** (−0.0564 and −0.0568 at 100) and lose most on long histories. They learn a 64-number embedding per item (15,901 items, about 16 answers each), whereas AKT learns one difficulty number per item; that is a likely reason, not a tested one.
3. **Time features add almost nothing**: SAINT+ against SAINT+ without time is +0.0008 ± 0.0005 AUC on ASSISTments 2009 (elapsed time only) and +0.0007 ± 0.0021 on the simulator (elapsed and lag time), far below the gate's +0.005.
4. **Longer windows do not help on this data.** AKT scores 0.7703, 0.7677 and 0.7691 at 50, 100 and 200, DKT 0.7554, 0.7555 and 0.7559. Half of the students have 24 answers or fewer.
5. **Calibration decides the gate.** With raw outputs AKT fails the T047 gate against DKT at every length, only because its ECE is worse by 0.023–0.035. After Platt scaling, two numbers fitted on the validation students that leave AUC unchanged, AKT passes: AUC +0.0122, worst slice +0.0020, ECE +0.0011 (both models calibrated). Against raw DKT, calibrated AKT is +0.0045 ECE on average but +0.0143 on one fold, so calibration fitted on 290 students is not yet stable.
6. **Simulator (synthetic, 600 students).** AKT 0.6801 ± 0.0069, DKT 0.6556 ± 0.0020, SAKT 0.6401, SAINT 0.5623, SAINT+ 0.5606. AKT passes the gate against DKT even with raw ECE (AUC +0.0245, ECE +0.0062, worst slice +0.0189). Within each model, the AUC gap between students with extra time and the others is smaller than its spread over folds (AKT −0.004 ± 0.012, DKT −0.010 ± 0.014). With about 2,100 extra-time answers per fold, that rules out a large unfairness but does not prove fairness. Dividing elapsed time by the time multiplier changed SAINT+'s AUC by +0.0002.
7. **Cost.** AKT is the most expensive to run. One request with a window of 100 takes a median 3.8 ms on one CPU thread (p95 4.4 ms); with 200 answers it takes 9.2 ms (p95 12.8 ms). At batch 64 with four threads it costs 0.87 ms per prediction at 100 answers and 7.6 ms at 200. DKT costs about a tenth of that. GPU latency is **pending**: there is no GPU before the cloud (S8+).

## Decision (proposed)

1. **Production knowledge-tracing model: AKT**, starting from pyKT's implementation (monotonic attention with distance decay and a Rasch difficulty per item), **followed by Platt calibration** fitted on held-out students and versioned with the model. Default window: **100 answers**. The gain from 200 is within noise, and 200 costs about 2.4 times more per request.
2. **Fallback: DKT**, trained in the same pipeline on every retrain and kept ready to serve. It is the best-calibrated model without any correction, the cheapest (about 0.4 ms per request on one thread) and the smallest. DKT becomes the champion if AKT fails the T047 gate on Kuizi data (T239), misses the latency budget (T046), or its calibration drifts (T050).
3. **SAINT+ is not chosen for now.** On the only real dataset available it is 0.069 AUC below AKT, and its time features add 0.0008. T239 re-tests it on Kuizi data, which will have lag time and more answers per item.
4. **The time and accommodation inputs planned for SAINT+ become gated experiments on AKT in T042.** They are elapsed and lag time divided by the time multiplier (T148) and an assistive-mode embedding. Each is kept only if it passes the T047 gate, including the accommodation slices, on Kuizi data.
5. **The IRT cold start (T043) stays.** On answers 2–10 the best model (AKT) beats DKT by only 0.0014–0.0021 AUC, and every model is worst calibrated there (ECE after Platt 0.034 for AKT, 0.027 for DKT).

## Still unknown

- **Kuizi data.** Bac Physics in French and Arabic, an item bank of at least 6,000 items, multi-concept and interactive items with partial credit, and about 2,000 pilot students. The ranking on US middle-school maths may not transfer.
- **A second public dataset.** ASSISTments 2017 needs the product owner to sign up and accept the ASSISTments terms (no sharing of the data, use only for the stated purpose, publish the code of any paper). ASSISTments 2015 is openly linked but has no item IDs or times. With one real dataset, the ranking rests on one population.
- **GPU latency and throughput.** Both are pending until a GPU exists (S8+). The CPU numbers come from one 4-core machine with batch 1 and 64, not a load test at 2,000 requests per second.
- **Time features on real data with timestamps.** ASSISTments 2009 has no lag time; the simulator is synthetic.
- **Accommodation fairness on real students.** No public dataset has accommodations; the simulator only shows that no model is grossly unfair.
- **Calibration stability.** Platt fitted on 290 validation students varied by fold (AKT ECE 0.003–0.020). Production needs a larger calibration set and monitoring (T050).
- **Tuning and training length.** No model was tuned individually, and AKT ran with `n_blocks = 1` (one knowledge-encoder layer and two retriever layers). On the simulator, AKT's best epoch was the 20-epoch limit in 2 of 3 folds, so its lead there may be understated.
- **The E05 target AUC ≥ 0.80.** No model reached it on ASSISTments 2009 under this protocol (best 0.7703). Whether it is realistic for Kuizi data is a T239 question.
- **Explanations (T049).** AKT exposes attention weights in its knowledge retriever, but the explanation design written for SAINT+ cross-attention must be adapted.

## How T239 re-checks this on pilot data

T239 reruns the same benchmark (`ml/benchmarks/kt_benchmark.py`, same protocol, folds by student, window lengths, slices and T047 gate with Platt calibration) on the pilot interactions. The pilot adapter from T041 replaces `load_dataset`, and the run happens in the cloud environment, never on a PC. The accommodation slices come from the learner comfort profile (T148) instead of the simulator, and the time-feature variants of AKT from T042 are added. Rule: AKT stays if, calibrated, it passes the T047 gate against DKT on pilot data; otherwise the best model that passes is proposed, and if none passes, DKT is champion. The product owner confirms the result in a new ADR that supersedes or confirms this one.

## Consequences

- If accepted, the backlog changes (the main session updates the backlog and Jira):
  - E05 goal: "self-hosted knowledge-tracing model (ADR 0007)" instead of "SAINT+".
  - T041: `make train MODEL=akt` (with `dkt` and `saint_plus` configs kept).
  - T042: production AKT with Platt calibration, plus time and accommodation features as gated experiments.
  - T046: serves AKT and DKT and adds the GPU latency measurement deferred from T040.
  - T049: explanations from AKT's attention.
  - The architecture overview reads "TorchServe KT model (AKT, ADR 0007)".
- Serving costs about ten times more CPU per prediction than DKT would. T046 sizes batching and workers (GPU or CPU) against p99 ≤ 50 ms.
- The calibrator is part of the model artefact; the champion/challenger gate (T047) compares calibrated models.
- Training stays cheap: an AKT run on ASSISTments 2009 took 2 to 8 minutes on one CPU thread.
- Rejected for now: SAINT+ and SAINT (lowest AUC on this data), SAKT (below DKT), DKT alone (best calibrated and cheapest, but 0.012 AUC lower; kept as the fallback).
