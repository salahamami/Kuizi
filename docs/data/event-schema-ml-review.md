# ML review of the learner event schemas (T023, acceptance criterion 3)

- Ticket: T023 (KK-43), criterion 3: "ML team signs off that the schema contains everything SAINT+ features need"
- Reviewer: ML Engineering agent, for the product owner's approval
- Date: 2026-10-18
- Reviewed: branch `feat/t023-event-schemas` at commit `14fe141` ([catalogue](event-catalogue.md), [`schemas/events/`](../../schemas/events/), [ADR 0009](../architecture/decisions/0009-learner-event-contracts.md))
- Scope: the inputs needed by every knowledge-tracing model still in play: AKT (proposed in [ADR 0007](../architecture/decisions/0007-knowledge-tracing-model.md)), DKT (fallback), SAINT+ (re-tested in T239), BKT, the IRT cold start (T043) and pilot calibration (T044). Also the accommodation-aware features (T148) and the slices of the T047 fairness gate.

## Verdict: signed off with conditions

Every model input in the review scope maps to a field that exists, with a type that fits. No field needs a different type or default, and none needs to be removed. I found nothing that would force a breaking change later. Four small fixes are needed before T023 merges (R1 to R4 below). They change documentation text and catalogue entries only, so compatibility is not affected. The other conditions are rules for later tickets, listed under "Conditions on later tickets".

The sign-off holds once R1 to R4 are in, and as long as the later tickets follow those rules.

## How it was checked

1. Read every schema in `schemas/events/` and `schemas/events/common/`, plus `catalogue.yaml`, `schemas/README.md`, the producer rules in `schemas/kuizi_schemas/examples.py`, ADR 0009 and the generated catalogue.
2. Read what the models consume: `ml/kuizi_brain/models.py` (`make_windows`, `SaintPlus`, `IRT`, `estimate_ability`), `ml/kuizi_brain/data.py`, `ml/benchmarks/kt_benchmark.py` (`build_windows`, slices, T047 gate rule), ADR 0007, `docs/architecture/neural-core.md`, tickets T041 to T050, T148, T221, T239, T070, T145, T036, T032, T033, and sections 3 and 4 of `docs/requirements/accessibility-focus-notifications.md`.
3. **Adapter probe.** I built the columns that `make_windows` and `build_windows` read (student, item, kc, correct, elapsed_s, lag_s, hints, time_multiplier, assistive) from the synthetic `item.answered` examples alone, with no join. The output is in the appendix. Everything was derivable. The probe also showed the ambiguity in the lag definition (R3a).
4. **Compatibility probe.** I applied candidate future changes to the expanded `item.answered` schema in memory and ran the project's Apache Avro checker (`kuizi_schemas.compat.check_pair`) in both directions. The output is in the appendix. Every addition in "Optional improvements" passes. Retyping or narrowing an existing field is refused, which is why the existing field shapes had to be right from the start.
5. Ran `make check` and `make schemas-check` (both pass; the hand-back has the output).

## Required before T023 merges

None of these changes a field's type or default.

| ID | Where | Change | Why |
| --- | --- | --- | --- |
| R1 | `catalogue.yaml` › `item.answered.required_envelope` | Add `session_seq`, giving `[client_ts, session_id, session_seq, device, app_version]`. The app takes the number from its session counter and sends it with the submit request; T221 copies it into the envelope. The field already exists (`["null", "int"]`, default `null`) and the examples already fill it. | The feature table sorts each learner's answers by `client_ts`, then `session_seq`. Only `session_seq` keeps the right order when the device clock jumps within a session (network time correction). It also lets T029 detect lost answers. Without the requirement, the sort key the table promises may be null on the main KT event. |
| R2 | `AccommodationContext.time_multiplier`, `doc` only (type `double` and default `1.0` unchanged) | Say what the value is: the multiplier **applied to this item's timers and hint timers for this event**. Drop the model rule from the doc ("Models divide elapsed and lag time by it") and say only that knowledge tracing uses it to normalise time features (T148). If the product owner wants attestation visible too, add `attested` (`boolean`, default `false`, sensitive) now or later; the change is compatible. | The current doc says "Official time multiplier attested by the school". T145 only requires attestation before *graded mock exams*, so practice timers may run with a multiplier that has not been attested yet. Models need the multiplier that actually shaped the timing data. Otherwise extra time on practice reads as slowness, which is the harm T148 exists to prevent. The registry cannot detect a change of meaning once data exists, so the wording has to be fixed now. Product owner question 1 confirms the T145 behaviour. If only attested multipliers ever apply, the two readings are the same and only the wording changes. |
| R3 | `catalogue.yaml` › `ml_features` notes (the generated page follows) | (a) **Lag time.** lag(i) = `presented_client_ts`(i) minus the latest `envelope.client_ts` among the learner's `item.answered` events with `client_ts` ≤ `presented_client_ts`(i). Any attempt and any activity count. Compute it **before** the training filters (attempt 1, activity). It is null for a learner's first item, and negative values (clock skew) are clamped to 0. (b) **Attempt.** Replace "like ASSISTments original == 1" with "like ASSISTments, whose `correct` is first-attempt correctness (`original == 1` removes scaffolding sub-problems, not retries)". (c) **When each input is known.** At presentation: item, concepts, lag, activity, subject, track, item language, accommodation. After the answer: correctness, score, elapsed, hints, confidence, first action, audio playback, timed out, misconception. The second group enters the model one step later. | (a) "The learner's previous `item.answered`" is ambiguous for retries. For attempt 2 the previous answer is attempt 1 of the same presentation, which gives a lag of −12.4 s on the example event (appendix). Filtering to attempt 1 first would count retry time as idle time. T028 and T048 must compute the same value. (b) The current wording is inaccurate. (c) The elapsed-time row already says this, but the hints and confidence rows do not. Feeding the hints used before attempt 1 into the prediction of that same attempt leaks the label, because hint use strongly predicts failure. |
| R4 | `catalogue.yaml` › `sensitive_readers` of `item.answered` and `item.presented` | Add T239 (benchmark on pilot data) and T045 (weekly retraining pipeline, which runs the training) to the tickets of "Knowledge-tracing training, through the restricted warehouse role". In `item.answered`, note that T048's cold rebuild from the warehouse also goes through the restricted role. | Only listed services may read the sensitive fields. T239's acceptance criteria require accommodation slices on pilot data, so T239 cannot meet them unless it is listed. |

## Answers to the data-engineering agent's questions

1. **One `item.answered` per attempt, attempt 1 by default: yes.**
   - The training target is `correct` on attempt 1, as in ASSISTments.
   - Later attempts are inputs only, never targets in the benchmark or the gate.
   - Hints shown before attempt 1 stay as inputs, shifted one step (R3c). T041 tests the ASSISTments variant "correct and no hint before the first answer" as an alternative label.
   - `response.kind = SKIPPED` stays in the sequence as its own response token. By default it is excluded from the loss and the metrics.

2. **Lag on device clocks: yes, keep `client_ts`. Never use `server_ts`.**
   - `server_ts` is wrong for offline replays, and for app events it is the time the SDK flushed its batch (T024), which compresses short gaps.
   - On one device the clock offset cancels out.
   - Across devices, an offset of a few seconds only matters for very short gaps. The feature is log-scaled (`log1p(lag/60)/8` in `kuizi_brain`), and a device switch rarely happens within a minute.
   - v1 rule: raw client clocks, negative values clamped to 0 (R3a). T029 already monitors client-to-server lag; if its p99 per session goes above 60 s, T028 and T048 add the same per-session skew correction.

3. **Elapsed time: `active_ms`, falling back to `latency_ms` when null.**
   - Time in the background (a call, a notification, another app) says nothing about knowledge, is heavy-tailed and is more common on phones, so it would bias the device slices.
   - Cap the feature at 600 s, as `load_assist2009` does.
   - Divide by the multiplier under consent (T148). The "thinking time" variant subtracts `audio_playback_ms`.
   - Keep `latency_ms` for data quality and as a candidate "time away" feature (`latency_ms − active_ms`).

4. **Partial credit: the label is `correct` (full credit) for every model, metric and the T047 gate.**
   - `score` is an input: a three-way response token (wrong, partial when 0 < score < 1, right).
   - In T042, a soft-label experiment (cross-entropy with target = `score`) is gated like any other feature.
   - No threshold at 0.5 by default. It would make the label depend on each item's rubric weights and shift the base rate by item type, and the champion and challenger must be compared on one fixed binary label.
   - Per-step credit tagged by concept would be better for multi-step items; see the optional `step_results` field.

5. **Multi-concept items: enough for v1.**
   - T041 expands multi-concept items as pyKT does (one row per concept, sharing the question ID), or uses a concept-set embedding for AKT. Putting the primary concept first gives a primary-only baseline.
   - Conditions D1 and D2: `item_version` is filled from the first real data and bumped by any change to KC tags or weights, and concept IDs are never reused with another meaning.
   - If T036 cannot guarantee that versioning, add `kc_weights` (`array<double>`, default `[]`, parallel to `kc_ids`). The probe shows it is compatible. Changing `kc_ids` itself into an array of records is refused.

6. **Null means standard conditions, including for an accommodated student who did not consent: acceptable, because it is the only lawful option.** Without consent the data cannot be processed, and a "consent withheld" flag would itself reveal that the student has an accommodation. The consequences have to be stated, not hidden:
   - (a) The T047 and T148 reports say that the standard slice contains an unknown number of accommodated students without consent, so fairness for them is not measured.
   - (b) Any in-item time feature (elapsed, first action, idle time) carries a residual, unmeasurable risk for these students. It ships only if it passes the T047 gate, and the model card states that risk. ADR 0007 measured +0.0008 AUC from time features on ASSISTments 2009 (elapsed time only) and +0.0007 on the simulator, so the proposed production AKT starts without them.
   - (c) The simulator in `kuizi_brain` and the T219 generator include accommodated students without consent (slower, null accommodation), so the harm can be measured on synthetic data.
   - (d) Whether the consent screen (T151) explains, without pressure, what sharing changes is a decision for the product owner and the DPO.

7. **`assistive_modes` as a list: yes, better than one value.**
   - A learner can use a magnifier and voice control at the same time.
   - The model uses a mean of mode embeddings (`EmbeddingBag`). An empty bag maps to a learned "none" vector, and the `UNKNOWN` that older readers get for a new mode maps to an "other assistive technology" vector.
   - Producers send the values sorted and de-duplicated, and never send `UNKNOWN` on purpose (D4).
   - T047 slices: each mode, plus "any assistive mode", with the small-group rule of requirements section 4.5.

8. **Hesitation threshold: no, keep 3 s fixed at emission.**
   - Scaling happens in the restricted feature pipeline: `idle_ms / multiplier`, or keep only `idle_ms > 3000 × multiplier`. This loses nothing: the multiplier is at least 1, so the scaled threshold is never below 3 s, and `idle_ms` is recorded.
   - Scaling at emission would leak the multiplier into a personal-class topic, through which hesitations exist at all.
   - Kuizi cannot hear screen-reader speech, so hesitation features of learners with `SCREEN_READER` are masked (set to missing) in the same pipeline. They are not suppressed at emission, because missing events would themselves reveal the mode.

## Feature-to-field check

Each row of the catalogue's knowledge-tracing table, checked against the schemas and against what the code consumes. "OK" means the field exists, its type fits, and the probe derived the input from `item.answered` alone where the row says so.

| # | Model input | Fields | Result | Notes for the consuming tickets |
| --- | --- | --- | --- | --- |
| 1 | Learner sequence and order | `envelope.student_id`, `client_ts`, `session_seq` | OK after R1 | T048 inserts each answer by (`client_ts`, `session_seq`, `server_ts`), not by Kafka offset: T221 instances can produce one learner's answers out of order, and offline answers arrive late. |
| 2 | Question ID | `item.item_id`, `item.item_version` | OK, condition D1 | AKT's Rasch difficulty and IRT a and b are per item. T041 benchmarks `item_id` alone against (`item_id`, `item_version`). Randomised variants of an interactive item (T036) share `item_id`, which suits knowledge tracing. |
| 3 | Concepts | `item.kc_ids` | OK, conditions D1, D2 | Question 5. The minimum of one concept is enforced in `examples.py`. |
| 4 | Correctness and partial credit | `correct`, `score` | OK | Question 4. `examples.py` enforces that correct means a score of 1.0 and that an incorrect answer scores below 1.0. Emit only graded answers (D4). |
| 5 | Elapsed time | `latency_ms`, `active_ms` | OK | Question 3. Known after the answer, so it enters one step later (as `SaintPlus` does). |
| 6 | Lag time | `presented_client_ts`, `envelope.client_ts` | OK after R3a | Question 2. The event definition is pure idle time and contains no part of the current answer's elapsed time, so it is known at presentation and leaks nothing. |
| 7 | Hints | `hints_used`, `max_hint_level`, `hint.requested:level`, `hint.shown:level` | OK after R3c | Tutor hints count too (`hint.shown.source = TUTOR`). Shift one step. The level *requested* (T070 criterion) is in `hint.requested`, which only the warehouse joins. On the online path (T048 reads `item.answered` alone), the shown level stands in for it. |
| 8 | Attempt number | `attempt` | OK after R3b | Question 1. |
| 9 | Confidence 1 to 5 | `confidence_1_5` | OK after R3c | Null means not asked, and the model uses a "missing" token. It is given after answering, so it enters one step later. |
| 10 | Time multiplier | `accommodation.time_multiplier`, `accommodation.untimed` | OK after R2 | Normalise in-item durations (elapsed, first action, idle). Whether lag is normalised too is product owner question 4. For untimed rows the multiplier means nothing: T148 masks in-item durations or uses `untimed` as an input, and the gate decides which. |
| 11 | Assistive modes | `accommodation.assistive_modes` | OK | Question 7. |
| 12 | Listening time | `audio_playback_ms`, `tts.played:played_ms` | OK | Join on `presentation_id` through `tts.played.item`. Screen-reader speech is not observable (question 8). |
| 13 | Timed out | `timed_out` | OK | Kept as incorrect (that is what happened) and flagged. T148 reports the timed-out rate per accommodation slice. Privacy observation 1 applies. |
| 14 | Activity | `item.activity` | OK | T043 seeds the estimate from `PLACEMENT`. T041 decides per activity: weight `MOCK_BAC` apart, and probably drop `DUEL` (opponent and time pressure). A `CALIBRATION` symbol for T044 can be added later (compatible). |
| 15 | Subject and section | `item.subject_id`, `item.track_id` | OK, condition D3 | T047 per-section AUC and T239 per-subject and per-track reports need them filled before the pilot. |
| 16 | Item language | `item.item_language` | OK | Also a T047 slice (D8): French and Arabic variants may differ in difficulty and in fairness. |
| 17 | Misconception code | `misconception_code` | OK | Known after the answer. |
| 18 | Hesitation, first action | `first_action_ms`, `item.hesitation:idle_ms`, `before_first_action` | OK | Question 8. If a hesitation feature passes the gate, add aggregates to `item.answered` so T048 still reads one topic (optional, compatible). |
| 19 | Interaction trace | `item.interaction:kind`, `value_from`, `value_to` | OK | T071, not knowledge tracing. The same aggregate approach applies if a feature passes the gate. |
| 20 | Session and Focus | `session.start:envelope.session_id`, `session.end:duration_ms`, `focus.end:reason` | OK | For knowledge tracing, the session boundary is available on `item.answered` itself (`session_id` is required there). |

**Inputs the table does not list, also checked:**

- **IRT cold start and calibration (T043, T044).** Ability is estimated per chapter. The chapter comes from the concept graph (T032 stores it as a KC attribute) through `kc_ids`. Distractor dominance uses `response.choice_ids`. The 200-response count per item uses attempt 1 per (`item_id`, `item_version`). Item a, b and c priors live in the item bank (T036), not in events. All of this is available.
- **T047 slices.**
  - Accommodation slices come from `AccommodationContext`, section from `track_id`, school from `tenant_id`.
  - Region and gender are deliberately absent from events: `gender`, `location` and similar names are forbidden by the house rules. They would come from the tenant and student dimensions. Product owner question 2 asks whether those slices stay.
  - I propose adding slices by item language and device form factor (`envelope.device`, required on `item.answered`).
- **Online calibration monitor (T047 criterion 2, T050).** The prediction made before an item is shown is not part of T023. `item.presented.routing_decision_id` is the join key. The prediction and model version belong in `routing.decision` (T052) or a new prediction event (T046), which would be a new topic and therefore compatible (D8).

## Conditions on later tickets

| ID | Owner (ticket) | Condition |
| --- | --- | --- |
| D1 | Product + Curriculum (T036) | `item_version` is filled from the first real data. Any change to an item's KC tags, tag weights or answer key bumps it. Otherwise the weight join by (`item_id`, `item_version`) is ambiguous. |
| D2 | Product + Curriculum (T032) | Concept IDs are never reused with another meaning. Splits and merges create new IDs plus a mapping that T041 can apply to history. |
| D3 | Product + Curriculum (T033) | `subject_id` and `track_id` are filled before the pilot. |
| D4 | Producers (T024 app SDK, T221 grading), validation (T025) | `active_ms` is filled whenever the client can measure it. `latency_ms` and `active_ms` come from a monotonic clock, not from wall-clock differences. `assistive_modes` is sorted, unique and never `UNKNOWN` on purpose. `session_seq` comes with the submit (R1). `item.answered` is emitted only once the answer is graded, never as an ungraded placeholder: the probe shows that making `correct` nullable later passes the registry but breaks every consumer still on v1. |
| D5 | T221, T028 | Regrades: the training key is (`presentation_id`, `attempt`). A regrade is a new event with a new `event_id` and a newer `grader_version`, and the latest grader wins. Reusing the `event_id` would make consumers drop the correction as a duplicate. |
| D6 | T219, with the ML Engineering agent | The ML team sets the target distributions (T219 criterion 2), which I will provide. They include accommodated learners without consent, multiple attempts, partial credit, skips, offline sessions with late `server_ts`, and clock offsets between a learner's devices. |
| D7 | ML Engineering (T041, T028 adapter, T048, T148) | The rules in the answers above: sort order, the lag definition (R3a), elapsed from `active_ms` capped at 600 s, label = attempt-1 `correct`, partial credit as an input, skips never a target, multi-concept expansion, after-the-answer inputs shifted one step (R3c), multiplier normalisation under consent, masking for untimed and screen-reader rows. T028 and T048 share one implementation of the time features. |
| D8 | ML Engineering (T046, T052, T047, T050) | A prediction log for the online calibration monitor, keyed by `routing_decision_id`. `routing.decision` logs the selection propensity for off-policy evaluation of routing (E06). Inference request logs never contain accommodation features. T047 adds slices by item language and device form factor. |

## Optional improvements

Each one is compatible in both directions (appendix). Add each when its consumer needs it, not now.

| Field | Type, default | When |
| --- | --- | --- |
| `item.answered.step_results` | `array<record StepResult {step_id: string, kc_ids: array<string> = [], score: double}>`, `[]` | When T221 grades multi-step derivations step by step. It gives per-concept evidence for multi-step items (T041 criterion 3). |
| `item.answered.kc_weights` | `array<double>`, `[]` (parallel to `kc_ids`) | Only if D1 cannot be guaranteed. |
| `item.answered.hesitation_count`, `idle_ms_total` | `int`, `0`; `long`, `0` | When a hesitation feature passes the T047 gate, so T048 stays on one topic. |
| `item.answered.tutor_messages_before` | `int`, `0` | If help-seeking beyond hints becomes a candidate feature (T042). |
| `Activity` symbol `CALIBRATION` | enum symbol | When T044 serves items in a fixed calibration sequence. |
| `ItemContext.variant_id` | `["null", "string"]`, `null` | When T036 generates randomised variants. T071 and regrades need the parameters that were shown. |
| `AccommodationContext.attested` | `boolean`, `false`, sensitive | If the product owner wants attestation visible (R2). |
| Presentation adaptations that change timing | for example `timer_hidden` (FR-A11 calm mode) and `split_into_steps` (FR-A10) on `item.presented` and `item.answered`, `boolean`, `false` | When T142 and T143 land, if T148 finds that they shift timing. The DPO decides their privacy class. |
| `item.answered.regrade_of_event_id` | `["null", uuid]`, `null` | If D5's "latest grader wins" rule is not enough. |

## Privacy observations (for the data-engineering agent and the DPO)

1. **The multiplier can be worked out exactly from personal-class timings.**
   - For a timed-out attempt, `latency_ms` ≈ `item.presented.time_limit_ms` × multiplier.
   - For a hint requested by the timer (`trigger = TIMER`, T070), `offset_ms` = the standard hint timer × multiplier.
   - The field-level rule ("never stored outside the sensitive record") holds, but this inference gets around it.
   - The schema cannot fix this without dropping the timing. The DPIA (T017, T151) should record it, and personal-class timings stay out of exports and small-group dashboards, which is already the rule.
2. **Suppressing hesitation events for screen-reader users at emission would itself reveal the mode.** That is why question 8 masks them in the restricted pipeline instead.

## Questions for the product owner

1. **T145.** Does a multiplier the school has not attested yet apply to practice timers? The answer settles R2's wording.
2. **T047 slices "by region, gender, school type".** No event carries gender or region, by design. Keep those slices, which need a lawful source in the student and tenant dimensions and a line in the DPIA? Or replace them with section, school (tenant), language, device and accommodation?
3. **T148, criterion 2.** "No item.hesitation event is emitted while assistive audio plays." Kuizi cannot observe third-party screen-reader speech. I propose rewording it to "while Kuizi audio plays or a voice command runs", with screen-reader learners' hesitation features masked in the model (question 8). This is a backlog change for the main session.
4. **Normalising lag time (requirements section 4.1).** The event defines lag as idle time between items, which measures forgetting, not speed. Dividing it by the multiplier would make an accommodated student's three-day gap look like two days. I propose normalising only in-item durations (elapsed, first action, idle) and keeping lag raw. The gate then decides between the two variants on T148 data. This deviates from the requirement text, so it needs your approval. Afterwards, the catalogue note on row 10 ("Elapsed and lag time are divided by the multiplier") follows your answer.

## Appendix: probe outputs

**Adapter probe.** Model inputs built from `schemas/events/examples/item.answered.json` alone, sorted per learner by (`client_ts`, `session_seq`, `server_ts`). Lag follows R3a, elapsed follows question 3, `thinking_s` subtracts `audio_playback_ms`, and `elapsed_norm_s` divides by the multiplier. Only the column spacing has been changed.

```
student   attempt  item                               kc                  n_kc  correct  score  elapsed_s  thinking_s  elapsed_norm_s  lag_s  hints  time_multiplier  assistive          activity
4a37fa2d  1        phys.mech.newton2.q0042@v3         mech.newton2        2     0        0.0    12.4       12.4        12.4            None   0      1.0              []                 PRACTICE
4a37fa2d  2        phys.mech.newton2.q0042@v3         mech.newton2        2     1        1.0    39.5       39.5        39.5            None   1      1.0              []                 PRACTICE
b9d8249e  1        phys.elec.rlc.resonance.q0007@v1   elec.rlc.resonance  1     1        1.0    95.0       81.0        63.3            None   0      1.5              ['SCREEN_READER']  MOCK_BAC
b9d8249e  1        phys.elec.rlc.derivation.q0011@v1  elec.rlc.resonance  2     0        0.5    158.0      136.0       105.3           5.0    0      1.5              ['SCREEN_READER']  MOCK_BAC

4 attempts, 3 kept for training (attempt 1)
```

With the catalogue's current wording ("previous `item.answered`"), the second row's lag would be 1793718030000 − 1793718042400 ms = −12.4 s, measured against attempt 1 of the same presentation. With R3a it is null, the same as attempt 1.

**Compatibility probe.** In-memory changes to the expanded `item.answered` schema, checked with `kuizi_schemas.compat.check_pair`. BACKWARD means the new schema reads old data, which is what the registry enforces (BACKWARD_TRANSITIVE). FORWARD means consumers still on the old schema read new data.

```
change                                                          BACKWARD (new reads old)    FORWARD (old consumers read new)
add kc_weights: array<double>, default []                       ok                          ok
add step_results: array<record>, default []                     ok                          ok
add hesitation_count: int, default 0                            ok                          ok
add AccommodationContext.attested: boolean, default false       ok                          ok
add Activity symbol CALIBRATION                                 ok                          ok
add ItemContext.variant_id: [null, string], default null        ok                          ok
add step_results WITHOUT default                                REFUSED                     ok
retype kc_ids: array<string> -> array<record{kc_id, weight}>    REFUSED                     BREAKS
narrow active_ms: [null, long] -> long                          REFUSED                     ok
widen correct: boolean -> [null, boolean]                       ok                          BREAKS
retype time_multiplier: double -> int                           REFUSED                     ok
retype score: double -> float                                   REFUSED                     ok
```

Both probes were one-off scripts run against the reviewed commit, on synthetic examples only, and are not committed.
