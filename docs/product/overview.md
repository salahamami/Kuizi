# Product overview

Kuizi is an adaptive tutor for the Tunisian Baccalauréat. It predicts, concept by concept, where each student will fail, and gives the shortest path to the grade they aim for.

## Personas

| Persona | Needs | Main screens |
| --- | --- | --- |
| Student (17–19) | Know what to study today, practise on real Bac material, get unstuck without being given the answer | 01–07 |
| Parent | Give consent, see plain-language progress, set screen-time limits, never a ranking against peers | 09 |
| Teacher | See class mastery live, act on alerts, assign sets and mock exams | 08 |
| School admin | Onboard classes, manage seats and licences, export reports | Portals (E11) |
| Curriculum author | Build the knowledge graph and item bank, review items | Authoring tools (E04) |
| Platform admin | Run tenants, support, moderation, feature flags | Admin console (E20) |

## Subjects and sections

Physics and Mathématiques at launch (S18), then Sciences (SVT / Chimie), Sciences techniques and Économie & Gestion (S19–S20), across the Bac sections Mathématiques, Sciences expérimentales, Sciences techniques and Économie & gestion.

## The core loop

Every action is recorded → the model updates what the student knows → the router picks the next step → the tutor helps → the result feeds back in. See [`../architecture/neural-core.md`](../architecture/neural-core.md).

## Advanced concepts and where they live

| Concept | What it does | Epic / tickets |
| --- | --- | --- |
| Deep knowledge tracing (proposed AKT, DKT fallback; ADR 0007) | Predicts the chance of failing each concept from the whole interaction history | E05 · T040–T049 |
| Cold start (IRT + 12-question placement) | First estimate before enough history | T043, T175 |
| Granular telemetry | Answers, hesitation, slider moves, confidence 1–5 | E03 · T023–T026 |
| Explainable predictions | Attention weights show what weighs on a concept | T049, T177 |
| Knowledge graph + adaptive routing | Goes back to the weak prerequisite instead of harder items | E06 · T052, T053 |
| Misconception diagnosis | Names the error behind a wrong answer | T071, T179 |
| Socratic tutor with hint ladder | Question → hint → worked step → solution after two attempts | E08 · T069, T070 |
| Curriculum-grounded answers + AI judge | Answers from official manuals; a second model blocks wrong physics | E07 · T061, T062 |
| 1-minute micro-remediation | Short interactive fixes, no passive video | T053, T179 |
| Spaced repetition tightened before the Bac | Reviews return just before forgetting | T054, T190 |
| Daily plan by coefficient and weakness | Splits study time across subjects | T057, T176 |
| Mock Bac, annales and grade estimate | Real papers, auto-grading, calibrated grade with uncertainty | E18 |
| Gamification by mastery gain | Rankings reward progress, not volume | E10 · T087, T088 |
| Teacher live heatmap + anomaly detection | Collective blockages, drop-off, suspicious patterns | T095, T096 |
| Parent summary written by AI | Weekly plain-language summary, judged before sending | T075 |
| Accessibility and accommodations | WCAG 2.2 AA, comfort profile, fair tracing | E14 |
| Focus and smart notifications | Silence while working, messages at the right moment | E15 |
| Native apps | iOS and Android with Apple Pencil, widgets, Live Activities | E16 |

The bilingual brief [`../deliverables/Kuizi-Concepts-EN-AR.pdf`](../deliverables/Kuizi-Concepts-EN-AR.pdf) explains these concepts in English and Arabic.
