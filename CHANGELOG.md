# Changelog

All notable changes to the Kuizi plan, backlog and documentation.

## 2026-10-24 — Re-plan for 6e–9e (ADR 0011): 24 sprints, free pilot from S10, paid launch in S24, the Bac in phase 2

The backlog follows [ADR 0011](docs/architecture/decisions/0011-start-with-6e-9e.md) and the three studies (`docs/curriculum/college-6-9-scope.md`, `docs/product/market-6-9.md`, `docs/requirements/minors-11-15.md`). Work done in the repository only; **Jira is not synced** (see "Pending Jira sync" below).

### Changed
- Totals: 20 → 21 epics, 241 → 275 tickets, 1,636 → 1,721 points (1,627 scheduled, 94 in Bac phase 2), 442 → 614 dependency links, 20 → 24 sprints.
- **Calendar:** free pilot with 3–5 partner private schools from S10 (2027-02-22; T108 pinned there, all its blockers in S9 or earlier), concours in S18 (S17–S18 left free for the change freeze and as a buffer), pilot exit review in S20 (T272), paid launch for 2027–28 in S24 (T110, from 2027-09-06) with 30-day hypercare. New phases (a ticket's phase now follows its sprint): 0 Foundations S1–S3, 1 Data Plane & Design Research S4–S6, 2 Intelligence & Pilot Build S7–S9, 3 Free Pilot & Product Surfaces S10–S14, 4 Concours Season & Hardening S15–S18, 5 Pilot Exit & Content Completion S19–S20, 6 Launch Readiness S21–S22, 7 Paid Launch 2027–28 S23–S24, 8 Bac (phase 2, not scheduled).
- **Pilot at S10 pulls the cloud work forward:** cloud tickets start in S6 instead of S8 (ADR 0006 said S8), after the data-residency decision (T247, S4), so the cloud move (T240) lands in S9, one sprint before the pilot.
- Sprint loads (points; capacity 13/40/65/80/95 then 134): S1 21, S2 39, S3 65, S4 78, S5 95, S6 101, S7 127, S8 134, S9 132, S10 132, S11 134, S12 133, S13 134, S14 106, S15 34, S16 11, S17 0, S18 0, S19 37, S20 47, S21 52, S22 5, S23 5, S24 5; Bac phase 2 94. S1 is over its planned 13 only because T040 was finished and pulled in.
- **Bac phase 2** (no sprint, label `phase-bac`): T035 (KK-55), T038 (KK-58), T079 (KK-99), T080 (KK-100), T081 (KK-101), T125 (KK-145), T126 (KK-146), and the new placeholder T274. Their dependents were re-pointed to 6e–9e work (T051 and T039 to T111, T044, T068 and T184 to T112, T085 to T178 and T220, T138 to T078, T178 and T108 no longer wait for T079).
- **Content re-scoped in place:** E13 becomes "Subject Coverage 6e–9e: Maths, Sciences, Arabic, French, English" (T111–T124, T127–T132 rewritten: maths 6e and 7e–9e graphs, 6e and 9e maths banks, sciences graphs and banks, Arabic, French, interactives, calibration, pilot releases 1 and 2 and the launch release); T033 (subject, level 6e–9e, concours weights, authoritative language), T039 (CNP textbooks in Arabic), T044 (maths calibration on the pilot), T233 (annual concours update). E18 becomes "Concours Mode: Mock Sixième & Neuvième, Writing Assessment & Score Estimate" (T184–T188, T190 rewritten; T187 is a band B opt-in estimate, none for band A). E09 is renamed "Interactive Learning Frontend: Web App, Item Player & Interactives" (T077 re-scoped to a 2D-first simulation core, 13 → 8). Epic goals rewritten for E02, E04, E07, E10, E12, E17, E19.
- **Age-band and legal rules** (minors-11-15.md 5.2): rewrites of T013 (parent-first consent, 5 → 8, Sprint 3 → 5), T069 (tutor by band), T084 (class battles, split), T087, T088 (class-only, opt-in, band B), T090 (no churn-risk model, 5 → 3), T096 (no individual cheating flags, 8 → 5), T154 (no send-time profiling, ML → backend, 8 → 3), T166 (no social sign-in for pupils), T169 (Kids Category and Families, 3 → 5), T170, T175, T176, T180, T181; criteria lines ("ADR 0011: …") added to 85 more tickets. T017 now starts from counsel's opinion (T242) instead of T013; T216 no longer waits for T107.
- **Market:** T200 brought forward (pilot schools signed in S5, by January 2027); T099 no longer waits for Stripe school billing and chooses the local rails in S14, checkout T194 and plans T195 (price tests as acceptance criteria) in S21; T104 and T109 sized for the concours season.
- **Splits before sprint entry:** T037 → T263, T042 → T264, T092 → T265 (13 → 8 + 5 each), T084 → T266.
- **Design gate:** 61 tickets that build what pupils, parents or teachers see are blocked by the approved design of their journey (T258, T260, T261, T262, T259, T244); the scheduler never puts a ticket in the sprint of its design approval.
- `tools/backlog/build_backlog.py`: horizon, phases and milestones from `additions.py`; phases follow sprints for every ticket and each epic's phase is the phase with most of its points; new tables `ADR11_CHANGES`, `DEPS` (with design-gate change lines), `TARGET_SPRINTS`; personas also read "As a pupil"; the backlog header, "What changed", architecture, roadmap, milestones and critical paths (now computed for the pilot and the launch) describe the 6e–9e plan.
- `tools/backlog/replan.py`: 24 sprints; pins the Sprint 1 and 2 tickets (done or in review), T108 in S10, T272 in S20 and T110 in S24; cloud from S6; a ticket is pulled earlier when a pinned ticket needs it; tickets planned from S19 are not pulled earlier; design-gate rule; capacity check per sprint.
- `docs/backlog/README.md` (files, plan after ADR 0011, sprint table to S24, label `phase-bac`) and `CLAUDE.md` (audience, horizon, minors' rules, cloud move in S9).

### Added
- Epic **E21 Design First: Research, Journeys & Cyanotype v2** and 34 tickets (145 points):
  - NEW-1 to NEW-12 of minors-11-15.md:
    - T242 (E02, 3 pts, S3): Counsel's opinion on the lawful route for processing pupils' data (11–15) under Law 2004-63 (articles 28 and 52)
    - T243 (E02, 5 pts, S3): Age bands in identity (A: 11–12, B: 13–15) and one policy table for every band rule
    - T244 (E02, 3 pts, S4): Child-facing privacy information and assent screens by band, and the parent notice (design with Legal / DPO)
    - T245 (E08, 5 pts, S8): As a pupil aged 11–12, I get help through suggested requests and the maths keypad, never a free-text chat (guided tutor, band A)
    - T246 (E07, 5 pts, S8): Personal-data filter and 30-day retention for band B tutor text before it reaches any provider
    - T247 (E01, 3 pts, S4): Data residency and cross-border transfers for children's data: hosting in Tunisia or AWS Paris with authorisation (ADR)
    - T248 (E03, 5 pts, S3): Telemetry policy by age band: allowed events and retention per band in the catalogue, the SDK and ingestion
    - T249 (E10, 3 pts, S7): Safe identity display: generated nicknames and preset avatars for pupils
    - T250 (E17, 3 pts, S8): As a pupil, I can reach a "J'ai besoin d'aide" button and the helplines from every screen
    - T251 (E20, 3 pts, S4): School-use file and the controller and processor roles in school contracts
    - T252 (E20, 2 pts, S2): Protocol for research and usability testing with children: consent, assent, two adults present, recording and deletion
    - T253 (E20, 2 pts, S5): Access policy and vetting for everyone who handles children's data
  - Design first (E21):
    - T254 (E21, 5 pts, S3): User research with pupils (11–15), parents and teachers: plan, interview guides, recruitment, synthesis
    - T255 (E21, 3 pts, S4): Experience vision and design principles for 11–15 (bands A and B), parent-first; journey maps for pupil, parent and teacher
    - T256 (E21, 3 pts, S4): Visual direction for 11–15 with a senior designer: two directions explored, one chosen
    - T257 (E21, 5 pts, S5): Core-journey prototype in Arabic and French (onboarding, Today, practice, help, parent summary) and usability round 1 with children
    - T258 (E21, 3 pts, S6): Usability round 2 with children and the approved design of the core pupil journey (design gate)
    - T259 (E21, 5 pts, S6): Cyanotype v2 foundations: spacing, type and colour scales, one icon family, Arabic-first typography, bidirectional maths rule
    - T260 (E21, 3 pts, S6): Approved design of the parent journey: account and consent, parent space, weekly summary, controls, plans and checkout (design gate)
    - T261 (E21, 3 pts, S7): Approved design of the teacher and school journey: classes and join codes, class view, assignments, writing review, school admin (design gate)
    - T262 (E21, 3 pts, S10): Approved design of concours mode: mock Sixième and Neuvième, writing tasks, past papers, score estimate (design gate)
  - Splits:
    - T263 (E04, 5 pts, S5): Item review workflow: review queue, approve or request changes with inline comments, second reviewer, publish
    - T264 (E05, 5 pts, S5): Time-aware features for the production model: elapsed-time and lag-time embeddings, hint use and confidence
    - T265 (E11, 5 pts, S6): Verify tenant isolation: cross-tenant attack suite across services and the RLS latency benchmark
    - T266 (E09, 5 pts, S13): As a band B pupil, I can duel a classmate I added with an in-person code; block and report, no matchmaking
  - Content:
    - T267 (E13, 8 pts, S13): Maths 7e–8e: item bank in Arabic (French alongside) for the prerequisites of the Neuvième and the whole year
    - T268 (E13, 8 pts, S13): English 6e–9e: concept graph and item bank for the Sixième and Neuvième papers (comprehension, language, written expression)
  - Writing assessment:
    - T269 (E18, 5 pts, S12): Writing tasks in the item model and player: the Arabic composition, the Sixième short writing tasks, a timed editor with autosave
    - T270 (E18, 8 pts, S13): Rubric scoring of Arabic and French writing with teacher review: official-style rubrics and a judged scorer, never final without a teacher
    - T271 (E18, 5 pts, S14): As a teacher, I review and confirm writing scores: queue, rubric marking, override and feedback to the pupil
  - Pilot exit, launch plan, Bac placeholder, mock papers:
    - T272 (E12, 5 pts, S20): Pilot exit review after the concours: learning gain, outcomes reported by the schools, satisfaction, go/no-go for the paid launch
    - T273 (E19, 3 pts, S20): Go-to-market plan for the September 2027 paid launch: schools for 2027–28, parent channels, concours calendar, prices from the tests
    - T274 (E13, 3 pts, Bac phase 2): Bac phase 2 plan: re-plan the Bac subjects (physics, maths, sciences, technique, éco/gestion) after the paid launch
    - T275 (E18, 5 pts, S14): Assemble mock Sixième and Neuvième papers in the official format (at least three of each), reviewed by teachers

### Questions for the product owner
1. **Counsel (T242, S3):** engaging Tunisian counsel is your call; an article 28 route that needs a family judge's authorisation per child could move the pilot whatever the plan says.
2. **Cloud from S6:** a pilot in S10 pulls the cloud foundation forward from S8 to S6 (about two more months of cloud cost). The alternative is a pilot in S11 (2027-03-08) with the cloud from S7. If the data-residency decision (T247) chooses hosting in Tunisia, the AWS foundation tickets need a re-plan.
3. **People:** a senior designer for the visual direction (T256) and a researcher or yourself for the sessions with children (T254, T257, T258).
4. **Rights:** reusing past Sixième and Neuvième papers and the CNP textbooks needs your approval (T039, T112, T115, T118, T119, T121, T122, T184, T233, T268, T275).
5. **Language content:** a content partner for Arabic, French and English, or authoring in-house (T235, T120–T122, T268)?
6. **Countdown:** the brief asks for the concours countdown on Today, the market study says "no countdowns, no fear". The plan shows the days left calmly, only to pupils who chose a concours, hidden in calm mode (T176, T170, T174). Confirm.
7. **Targets to confirm:** the load test at 20,000 concurrent pupils with a capacity model to 50,000 (T104); writing scores agreeing with teachers at quadratic weighted kappa ≥ 0.7 (T270); the score estimate within 1.5 points (T187).
8. **Pilot scope:** 6e and 9e classes with maths at the start (T130), sciences and the language subjects from S10–S13 and the mock concours in S15 (T131). Today (T176, S12), the parent summary (T075, S13) and the parent space (T097, S14) arrive after the pilot starts. Acceptable?
9. **Scope reductions to confirm:** T090 (no churn-risk model, 5 → 3), T096 (no individual cheating flags, 8 → 5), T154 (no send-time model, 8 → 3, backend), T077 (2D-first simulation core, 13 → 8); physical sciences of 7e–9e (examined in neither concours) and the 9e technique track wait for the 2027–28 roadmap (T132).
10. **Phase names** for the 24-sprint plan (S21–S22 "Launch Readiness", S23–S24 "Paid Launch 2027–28", and the renamed phases 1–5), the Jira project name (still "Kuizi Adaptive Bac Platform") and keeping the label `persona-student` for pupils.
11. **Load profile:** S7–S14 sit at the 134-point ceiling and S15–S18 are light (S17–S18 empty for the concours freeze). After the S1–S2 velocity reset, rerun `tools/backlog/replan.py`; a velocity well below 134 moves the pilot unless scope is cut.
12. Still open from earlier: ADR 0007 (the model behind T042), and the conflicts between `accessibility-focus-notifications.md` and the minors rules (minors-11-15.md 5.4); the backlog applies the stricter MR-* rules in the criteria.

### Not changed in this re-plan
- T012 and T023 are in review and were not reopened; their follow-ups are T243 (age bands) and T248 (telemetry by band). Documentary Bac wording left in descriptions that are otherwise valid: T220 ("annales and the mock Bac"), T136, T219's description (its criteria line covers 11–15).
- Documents that still describe the Bac and belong to other sessions (minors-11-15.md 5.4): `README.md`, `docs/product/overview.md`, `docs/dev/identity.md`, `docs/data/event-catalogue.md` and `schemas/events/catalogue.yaml`, the role briefs in `.claude/agents/`, `docs/product-owner-decisions.md`, `docs/requirements/accessibility-focus-notifications.md`.

### Pending Jira sync
Jira was not touched in this session. To apply (procedure in `docs/backlog/README.md`, path A), all from `docs/backlog/apl_backlog.json`:
1. **Create** epic E21 and T242–T275 (children of their epics, assignee the product owner, labels and points from the JSON plus `sprint-NN` and `phase-N`; T274 without a sprint, label `phase-bac`); add their rows to `docs/backlog/jira_keys.csv` and rerun the generator.
2. **Create sprints** APL Sprint 21 (2027-07-26 → 2027-08-06), 22 (2027-08-09 → 2027-08-20), 23 (2027-08-23 → 2027-09-03) and 24 (2027-09-06 → 2027-09-17); record their IDs in `docs/backlog/README.md`. **Update every sprint goal** (S1–S24): the phase and the three epics with the most points (S17–S18: concours change freeze and buffer).
3. **Epics:** rename KK-9 (E09), KK-13 (E13), KK-18 (E18); rewrite the goal and Definition of Done of KK-2, KK-4, KK-7, KK-10, KK-12, KK-17, KK-19; refresh the Scope line of all epics.
4. **Rewrite** summary, description and points of T013 (KK-33), T033 (KK-53), T037 (KK-57), T039 (KK-59), T042 (KK-62), T044 (KK-64), T057 (KK-77), T069 (KK-89), T077 (KK-97), T084 (KK-104), T085 (KK-105), T087 (KK-107), T088 (KK-108), T090 (KK-110), T092 (KK-112), T096 (KK-116), T099 (KK-119), T104 (KK-123), T108 (KK-127), T109 (KK-128), T110 (KK-129), T111 (KK-130), T112 (KK-131), T113 (KK-132), T114 (KK-133), T115 (KK-135), T116 (KK-136), T117 (KK-137), T118 (KK-138), T119 (KK-139), T120 (KK-140), T121 (KK-141), T122 (KK-142), T123 (KK-143), T124 (KK-144), T127 (KK-147), T128 (KK-148), T130 (KK-150), T131 (KK-151), T132 (KK-152), T145 (KK-165), T153 (KK-173), T154 (KK-174), T159 (KK-179), T166 (KK-186), T169 (KK-189), T170 (KK-190), T172 (KK-192), T174 (KK-194), T175 (KK-195), T176 (KK-196), T178 (KK-198), T180 (KK-200), T181 (KK-201), T184 (KK-204), T185 (KK-205), T186 (KK-206), T187 (KK-207), T188 (KK-208), T190 (KK-210), T194 (KK-214), T195 (KK-215), T200 (KK-220), T233 (KK-253). Points change: T013 5→8, T037 13→8, T042 13→8, T077 13→8, T084 13→8, T090 5→3, T092 13→8, T096 8→5, T112 13→8, T115 13→8, T118 13→8, T121 13→8, T123 13→8, T124 13→8, T154 8→3, T169 3→5. T154's agent label becomes `agent-backend`.
5. **Refresh descriptions** (criteria added) of KK-35, KK-37, KK-38, KK-40, KK-42, KK-44, KK-45, KK-46, KK-50, KK-56, KK-67, KK-69, KK-74, KK-75, KK-79, KK-82, KK-83, KK-84, KK-86, KK-88, KK-90, KK-92, KK-93, KK-94, KK-95, KK-109, KK-111, KK-113, KK-114, KK-115, KK-117, KK-118, KK-120, KK-122, KK-154, KK-155, KK-161, KK-163, KK-164, KK-166, KK-170, KK-171, KK-172, KK-175, KK-177, KK-178, KK-180, KK-181, KK-183, KK-184, KK-187, KK-188, KK-197, KK-202, KK-203, KK-211, KK-212, KK-213, KK-216, KK-217, KK-218, KK-219, KK-221, KK-223, KK-224, KK-225, KK-227, KK-228, KK-229, KK-235, KK-236, KK-239, KK-240, KK-242, KK-243, KK-244, KK-245, KK-246, KK-247, KK-248, KK-249, KK-250, KK-256, KK-259, KK-260.
6. **Move to a new sprint** (153; update `sprint-NN`, `phase-N` and the description): KK-21 S8→S6, KK-22 S8→S6, KK-23 S9→S7, KK-24 S9→S7, KK-25 S10→S8, KK-27 S10→S8, KK-28 S11→S9, KK-30 S11→S9, KK-31 S10→S8, KK-33 S3→S5, KK-35 S10→S8, KK-36 S10→S8, KK-39 S11→S9, KK-40 S15→S21, KK-41 S9→S7, KK-42 S10→S8, KK-44 S3→S4, KK-51 S11→S9, KK-53 S3→S2, KK-54 S4→S5, KK-64 S10→S13, KK-65 S11→S9, KK-67 S12→S10, KK-69 S9→S10, KK-70 S13→S11, KK-73 S9→S10, KK-74 S10→S11, KK-75 S10→S11, KK-76 S9→S10, KK-77 S11→S12, KK-80 S10→S8, KK-83 S9→S10, KK-84 S8→S9, KK-85 S8→S9, KK-86 S9→S10, KK-90 S8→S9, KK-92 S9→S10, KK-94 S9→S10, KK-97 S5→S9, KK-98 S6→S9, KK-102 S8→S9, KK-106 S11→S9, KK-107 S9→S10, KK-109 S10→S11, KK-113 S12→S8, KK-114 S14→S19, KK-118 S15→S20, KK-119 S15→S14, KK-120 S16→S20, KK-121 S11→S9, KK-122 S12→S10, KK-124 S15→S16, KK-125 S16→S21, KK-126 S16→S15, KK-127 S12→S10, KK-128 S17→S16, KK-129 S18→S24, KK-130 S8→S3, KK-131 S11→S6, KK-132 S12→S7, KK-133 S9→S7, KK-135 S13→S10, KK-136 S13→S11, KK-137 S10→S5, KK-138 S14→S8, KK-139 S14→S11, KK-140 S12→S9, KK-141 S15→S12, KK-142 S15→S12, KK-143 S9→S11, KK-144 S12→S13, KK-147 S15→S14, KK-148 S16→S19, KK-149 S16→S20, KK-150 S18→S10, KK-151 S19→S15, KK-152 S20→S23, KK-153 S4→S7, KK-155 S6→S7, KK-156 S8→S9, KK-158 S10→S11, KK-159 S7→S10, KK-160 S12→S10, KK-161 S11→S9, KK-163 S13→S12, KK-164 S13→S12, KK-165 S9→S10, KK-167 S12→S10, KK-168 S8→S10, KK-169 S12→S10, KK-170 S13→S14, KK-171 S11→S9, KK-172 S10→S11, KK-174 S14→S13, KK-176 S14→S15, KK-177 S13→S12, KK-179 S14→S13, KK-182 S5→S6, KK-183 S7→S11, KK-184 S8→S12, KK-185 S10→S12, KK-186 S7→S12, KK-187 S8→S12, KK-188 S15→S21, KK-189 S15→S21, KK-190 S15→S19, KK-191 S15→S19, KK-192 S15→S20, KK-193 S16→S21, KK-194 S4→S7, KK-198 S9→S8, KK-199 S13→S12, KK-201 S13→S12, KK-202 S13→S12, KK-204 S14→S13, KK-205 S15→S13, KK-206 S14→S13, KK-208 S15→S14, KK-209 S16→S15, KK-210 S16→S15, KK-211 S8→S9, KK-213 S14→S13, KK-214 S16→S21, KK-215 S16→S21, KK-217 S17→S22, KK-218 S14→S12, KK-219 S16→S22, KK-220 S15→S5, KK-222 S10→S8, KK-223 S13→S12, KK-224 S16→S14, KK-225 S16→S14, KK-226 S16→S15, KK-227 S10→S8, KK-228 S15→S14, KK-230 S14→S13, KK-231 S9→S7, KK-232 S9→S7, KK-233 S10→S8, KK-235 S3→S4, KK-236 S16→S8, KK-237 S9→S7, KK-238 S10→S8, KK-243 S9→S8, KK-244 S9→S8, KK-246 S15→S14, KK-247 S16→S14, KK-248 S16→S20, KK-249 S13→S14, KK-250 S9→S13, KK-253 S19→S20, KK-259 S14→S19, KK-260 S11→S9. Tickets that keep their sprint but change phase label also need the label and description refreshed (phase names changed).
7. **Move to Bac phase 2** (remove from the sprint and the `sprint-NN` label, add `phase-bac`): KK-55 (T035), KK-58 (T038), KK-99 (T079), KK-100 (T080), KK-101 (T081), KK-145 (T125), KK-146 (T126).
8. **Remove 50 obsolete links** (by hand; blocker → blocked): KK-33→KK-37, KK-55→KK-59, KK-58→KK-64, KK-55→KK-71, KK-58→KK-88, KK-99→KK-105, KK-100→KK-105, KK-101→KK-105, KK-75→KK-110, KK-109→KK-110, KK-118→KK-119, KK-99→KK-127, KK-127→KK-129, KK-128→KK-129, KK-54→KK-130, KK-130→KK-132, KK-54→KK-133, KK-57→KK-135, KK-53→KK-137, KK-54→KK-137, KK-57→KK-138, KK-59→KK-139, KK-137→KK-139, KK-54→KK-140, KK-57→KK-141, KK-59→KK-142, KK-140→KK-142, KK-131→KK-148, KK-138→KK-148, KK-77→KK-150, KK-127→KK-150, KK-132→KK-150, KK-143→KK-150, KK-129→KK-151, KK-136→KK-151, KK-138→KK-151, KK-144→KK-151, KK-145→KK-151, KK-148→KK-151, KK-141→KK-152, KK-142→KK-152, KK-146→KK-152, KK-99→KK-158, KK-62→KK-168, KK-50→KK-174, KK-99→KK-198, KK-58→KK-204, KK-127→KK-220, KK-126→KK-236, KK-129→KK-253.
9. **Add 222 links**: 172 involve the new tickets (their blockers and blocks are in the JSON); the 50 between existing issues are KK-130→KK-59, KK-127→KK-64, KK-131→KK-64, KK-138→KK-64, KK-130→KK-71, KK-131→KK-88, KK-132→KK-91, KK-198→KK-105, KK-240→KK-105, KK-172→KK-110, KK-178→KK-110, KK-150→KK-127, KK-195→KK-127, KK-198→KK-127, KK-220→KK-127, KK-227→KK-127, KK-236→KK-127, KK-244→KK-127, KK-152→KK-129, KK-214→KK-129, KK-215→KK-129, KK-137→KK-132, KK-130→KK-137, KK-133→KK-139, KK-53→KK-142, KK-141→KK-147, KK-139→KK-148, KK-142→KK-148, KK-59→KK-150, KK-72→KK-150, KK-138→KK-150, KK-77→KK-151, KK-141→KK-151, KK-142→KK-151, KK-150→KK-151, KK-205→KK-151, KK-206→KK-151, KK-143→KK-152, KK-144→KK-152, KK-148→KK-152, KK-253→KK-152, KK-98→KK-158, KK-173→KK-174, KK-131→KK-204, KK-138→KK-204, KK-151→KK-207, KK-131→KK-253, KK-135→KK-253, KK-138→KK-253, KK-139→KK-253.

## 2026-10-23 — UI kits proposed; final Lab design on the canvas

- Proposed UI kits (decision waiting for the product owner, see `docs/product-owner-decisions.md`): shadcn/ui on Radix and Tailwind for the web, React Aria Components for complex widgets (ordering, sliders, drag and drop), Material 3 for Android, Apple's iOS UI Kit for iPhone; Lucide, MathLive and KaTeX as add-ons. Cyanotype stays the look.
- Design canvas: new page "Version finale" with screen 04 · Labo as it will ship, on web (French and Arabic switch, live pendulum simulation whose period follows T₀ = 2π√(L/g), answer choices, confidence 1–5, tutor hint ladder that opens level 3) and on phone (Arabic first, tutor as a bottom sheet). `docs/design/design-system.md` says so.
- No backlog or Jira change.

## 2026-10-18 — T076 split before Sprint 3 (new ticket T241)

T076 was 13 points, and the conventions split anything at 13 before sprint entry.

### Changed
- **T076 (KK-96)** is now "Next.js 15 app foundation: apps/web with the App Router, i18n (ar/fr) with RTL and Keycloak sign-in", 8 points, still Sprint 3. Its description follows ADR 0008 (pnpm workspace instead of Turborepo), and its third acceptance criterion is now Keycloak sign-in (PKCE) with roles and tenant read from the token.
- **New T241 (KK-261)** "Shared UI package and Storybook: packages/ui, stories in French and Arabic, accessibility checks, Storybook for every pull request", 5 points, Sprint 3, frontend agent, blocked by T076. It blocks T174, which now also lists it as a blocker.
- Sprint 3 keeps 65 points (now 11 tickets). Totals: 241 tickets, 1,636 points, 442 dependency links.
- `tools/backlog/build_backlog.py` reads a new `SPLITS` table in `additions.py`: the fields it gives replace the v1 ticket's, and a change line records the split.

### Jira sync
- KK-96: summary, description and story points (13 → 8) updated.
- KK-261 created: Tâche, child of KK-9 (E09), APL Sprint 3, 5 points, labels `agent-frontend`, `apl-t241`, `sprint-03`, `phase-0`, `storybook`, `design-system`, `frontend`; assigned to the product owner. Links: KK-96 blocks KK-261, KK-261 blocks KK-194.
- Descriptions refreshed for the 13 tickets blocked by T076 (KK-97, KK-103, KK-104, KK-106, KK-122, KK-153, KK-155, KK-157, KK-182, KK-194, KK-240, KK-244, KK-252) and the scope line of KK-9.
- `docs/backlog/jira_keys.csv`: new row `T241,KK-261`.

## 2026-10-18 — Sprint 2 started early: CI, identity, learner events, concept graph, brand

While Sprint 1 waits for the product owner's review, the five Sprint 2 tickets were started early ("work ahead"); they stay in APL Sprint 2 in Jira. Each was handed to the agent of its role, worked in its own git worktree and branch, reviewed by the main session and merged into `feat/sprint-2`. The backlog itself (scope, points, sprints, links) did not change.

### Added
- **ADR 0008 (proposed): monorepo layout and toolchains.** Folders `apps/`, `services/`, `packages/`, `schemas/`, `curriculum/`, `brand/`; Node 22 with pnpm workspaces, strict TypeScript, ESLint, Prettier, Vitest; Python 3.12 with uv, Ruff, pytest. Root tooling: `package.json`, `pnpm-workspace.yaml`, `tsconfig.base.json`, `eslint.config.js`, `.prettierrc.json`.
- **T006 CI (KK-26, platform-devops agent).** GitHub Actions with project discovery (`scripts/ci/discover.py`): reusable Python, TypeScript and container workflows; coverage gates (services 80 %, frontends 70 %, `ml/` 75 %); Pact convention (`test:contract`); Syft SBOM, Trivy gate on CRITICAL, cosign keyless signing and SBOM attestation on `main` only (GHCR until T240); actions pinned to commit SHAs (new check in `make check`); `make lint` and `make test`; root `ruff.toml`; 50 pytest tests for `ml/kuizi_brain`. Guide: `docs/dev/ci.md`. Median run 59 s on GitHub. After the merge with the other tickets, CI also builds each image from its own folder (opt-in `# kuizi-ci: context=repo-root`), starts PostgreSQL for projects that ask for it (`[tool.kuizi.ci] services = ["postgres"]`, so the concept-graph database tests are mandatory in CI), and runs the schema compatibility check on the full git history (`full-history`, `checks`).
- **T012 identity (KK-32, backend agent).** One Keycloak realm `kuizi` (single issuer) with roles, `tenant_id` and `roles` claims, 15-minute access tokens, rotating refresh tokens, brute-force protection, French and Arabic; a Kuizi Keycloak image with a Have I Been Pwned password policy (k-anonymity) and a login theme with 44 px controls; `@kuizi/auth` verifies tokens in services (55 tests). ADR 0009 (proposed). Guide and screenshots: `docs/dev/identity.md`. **Keycloak moved from 26.1.4 to 26.8.1** because the CI Trivy gate found 7 CRITICAL vulnerabilities in stock 26.1.4 (among them an unauthenticated account takeover, CVE-2026-18963) that no 26.1 release fixes; 26.8.1 scans at 0 CRITICAL and 0 HIGH. The upgrade migrates the local `keycloak` database one way: an older image no longer starts on it (`make reset` or recreate that database).
- **T023 learner events (KK-43, data-engineering agent; ML sign-off by the ml-engineering agent).** 15 Avro events with a shared envelope, one topic per event, BACKWARD_TRANSITIVE compatibility enforced by the registry and by an offline check against git history; privacy class on every field, sensitive accommodation fields only in `AccommodationContext`, no free text in `tutor.message`; machine-readable catalogue and generated page `docs/data/event-catalogue.md`; 125 tests. ADR 0010 (proposed). ML review `docs/data/event-schema-ml-review.md`: signed off with conditions R1–R4, all applied.
- **T032 concept graph (KK-52, product-curriculum agent; tests run by the main session).** PostgreSQL schema `curriculum` with ltree paths, KCs shared across tracks with per-track chapter and exam weight, typed edges and a cycle-rejecting trigger that holds under concurrent writes; starter Physics seed (70 KCs, 132 edges, 4e Mathématiques, Sciences expérimentales, Sciences techniques, all `to_review`); loader and JSON export with its JSON Schema; 50 tests. Doc: `docs/curriculum/kc-graph.md`.
- **T231 brand (KK-251, design-ux agent; rendered and checked by the main session).** Eight-point star mark with a rhombus counter, logotypes «kuizi» and «كويزي» drawn as shapes (geometric Kufi), lockups, iOS, Android and web icons, social images; `brand/export.json` and 67 rendered PNGs plus `favicon.ico`; brand guide (draft) and review briefs for an Arabic type designer and a trademark search: `docs/design/brand-guide.md`, `docs/design/brand-reviews.md`.
- `docs/product-owner-decisions.md`: every decision waiting for the product owner, grouped by urgency and ticket, with the acceptance-criteria wording the agents proposed (not applied).

### Changed
- `infra/local/compose.yaml`: Keycloak is built from `services/keycloak` (`pull_policy: never`). `.env.example` gains `KEYCLOAK_API_AUDIENCE` and the Google sign-in variables (empty).
- `ml/`: six files reformatted by Ruff and small lint fixes; the T040 benchmark records a new `code_sha256` from now on.
- `Makefile`: `lint`, `test`, `graph-*` and `schemas-*` targets.
- `docs/STATUS.md`, `README.md`, `docs/README.md`, `docs/dev/local-setup.md`: links to the new guides.

### Jira sync
- KK-26, KK-32, KK-43, KK-52 and KK-251 moved À faire → En cours → Revue en cours, each with a comment on what was built, how each acceptance criterion was verified and what waits for the product owner. They stay in APL Sprint 2. No scope, point, sprint or link change, so `additions.py` and the generated backlog are unchanged.

## 2026-10-18 — Session hand-off: status page and documentation rule

### Added
- `docs/STATUS.md`: the page every session starts from — Sprint 1 state, decisions waiting for the product owner, next work, how a new session continues (Jira IDs, transitions, story-point field), environment notes for Claude sessions.

### Changed
- `CLAUDE.md`: sessions start with `docs/STATUS.md`; new rule "Always keep the documentation updated" (update STATUS, CHANGELOG and every changed `.md` file, commit and push, before a session ends).
- `README.md` and `docs/README.md` link the status page. The sprint table in `docs/backlog/README.md` shows Sprint 1 with 4 tickets (21 points) and Sprint 2 with 5 (29) after T040 moved forward.
- `docs/architecture/overview.md` and `neural-core.md` no longer present SAINT+ as decided: the model is chosen in ADR 0007 (proposed AKT, DKT fallback). Same fix in `README.md` and `docs/product/overview.md`.
- `ml/README.md`: EdNet is no longer listed as an allowed dataset (CC BY-NC licence).

## 2026-10-18 — T040 knowledge-tracing benchmark (Sprint 1, in review)

Done by the `ml-engineering` agent; reviewed by the main session (self-checks rerun, results files and ADR checked).

### Added
- `ml/benchmarks/`: `kt_benchmark.py` (5-fold split by student, quick and full modes, Platt calibration, T047 gate, CPU latency, MLflow logging), `check_kt_benchmark.py` (self-checks), `t040_benchmark.ipynb` (tables and charts from the saved results), `results/` and a README.
- ADR 0007 (Proposed): AKT with Platt calibration and 100-answer windows as the production knowledge-tracing model, DKT as the fallback. The product owner decides.

### Findings (ASSISTments 2009, 3 folds of 726 unseen students, windows of 100)
- AUC: AKT 0.768 ± 0.003, DKT 0.756 ± 0.002, SAKT 0.719, SAINT 0.699, SAINT+ 0.699. CPU latency at batch 1: AKT 3.8 ms, DKT 0.4 ms.
- AKT beats DKT by +0.012 AUC with no slice worse, but fails the T047 gate on raw calibration (ECE 0.040 vs 0.005); it passes after Platt calibration.
- SAINT+'s time features add +0.0008 AUC; windows longer than 50 answers do not help.
- On simulated students AKT also leads (0.680 vs 0.656); no model shows an extra-time gap larger than its spread, which rules out a large unfairness but does not prove fairness.
- ASSISTments 2017 needs a sign-up and acceptance of terms by the product owner; not used. GPU latency waits for the cloud (S8+).

### Jira sync
- KK-60 moved to *Revue en cours* with a comment.

### Pending decision (product owner)
- Accept ADR 0007 or keep DKT as champion until T239. If accepted, the backlog and Jira change for E05's goal, T041, T042 (AKT instead of SAINT+), T046 (serve AKT and DKT, GPU latency moved from T040), T049, and the architecture overview.

## 2026-10-18 — T234 agent operating model (Sprint 1, in review)

### Added
- `.claude/agents/`: 14 role briefs, one per `agent-*` label, written as Claude Code agent definitions: mission, what the role owns, tools and stack, role-specific done checks, what it must never do, when to ask the product owner, shared ground rules and the hand-back format. Each role gets only the tools it needs (document roles cannot run shell commands; no agent has Jira or repository-settings tools).
- `docs/process/working-agreement.md`: who does what, Definition of Ready and Done, review gates, branch and pull-request rules, ADR process, sprint rhythm, how to start a task with an agent. `docs/agents/README.md` lists the roles.
- `.github/pull_request_template.md` (Definition of Done checklist) and `.github/CODEOWNERS`.
- `make check` (`scripts/check_repo.py`): checks the compose file, the briefs' front matter, that every `agent-*` label has a brief, and that the generated backlog is up to date, without changing any file. Written by the `qa-sdet` agent from its brief alone, as the test of the operating model.

### Changed
- T234 acceptance criteria: "staging" becomes "tested on the local stack" (ADR 0006), and branch protection is described as it can work while every agent pushes with the product owner's GitHub account (the product owner's merge is the approval; a required code-owner approval comes once agents use their own account).
- `CLAUDE.md` points to the briefs and the working agreement and states that agents never merge, deploy or change settings.

### Jira sync
- KK-254: description updated, links to the briefs and the working agreement added, moved to *Revue en cours* with a comment.

### Pending (product owner, on GitHub)
- Protect `main`: Settings → Branches → rule for `main` with "Require a pull request before merging", "Block force pushes", "Restrict deletions" and no bypass. The connector cannot change repository settings.

## 2026-10-18 — T238 brain walkthrough (Sprint 1, in review)

### Added
- `ml/notebooks/`: ten notebooks, each in English and Arabic, from the concept graph to SAINT+ and fairness. Every code cell names its concept and the production ticket that will build it. All ten run end to end on CPU; the longest (07, SAINT+) takes about 5 minutes on 4 cores.
- `ml/kuizi_brain/`: small teaching library: Bac Physics concept slice with French and Arabic names, ASSISTments 2009 loader (fingerprint-checked download), Bac Physics student simulator with known true mastery and accommodations, IRT with Bayesian cold start and adaptive placement, BKT, DKT, SAINT+, mastery probes with attention, AUC and calibration.
- `docs/brain/README.md` (index, data and licences) and `docs/brain/glossary.md` (57 terms in English, Arabic and French).

### Findings worth carrying into T040
- On ASSISTments 2009 (students never seen in training): BKT AUC 0.726, DKT 0.756, SAINT+ 0.710. On the simulator: DKT 0.662, SAINT+ 0.624, ceiling 0.742. This matches published benchmarks: SAINT-type models need very large datasets. T040 and T239 should decide the production model on data, and DKT must stay in the benchmark.
- Time features did not help SAINT+ on the simulator (0.624 with, 0.645 without); T040 should test them on real data.
- A speed-only mastery signal underestimates students with extra time (bias −0.022 against +0.005 for the others); dividing time by the multiplier reduces it to −0.006 (T148).
- Splitting by answer instead of by student inflates IRT's AUC from 0.630 to 0.746 (leakage): T040 must split by student.

### Jira sync
- KK-258 moved to *Revue en cours* with a comment; the review session with the product owner closes it.

## 2026-10-17 — Sprint 1 starts now

The product owner decided not to wait for November: Sprint 1 started on 2026-10-17 and ends on 2026-10-30. Every sprint moves two weeks earlier, so S2 starts 2026-11-02, the pilot (S12) runs 2027-03-22 to 2027-04-02, go-live (S18) 2027-06-14 to 2027-06-25, and S20 ends 2027-07-23. Scope, points and sprint contents are unchanged.

### Changed
- Generator: `SPRINT_START` is 2026-10-19 (the Monday of the first sprint week); `CLAUDE.md`, `README.md` and the sprint table in `docs/backlog/README.md` show the new dates.

### Jira sync
- Updated the dates of `APL Sprint 1` to `APL Sprint 20` (goals unchanged) and started `APL Sprint 1`: it is the active sprint, with KK-254, KK-257 and KK-258.

## 2026-10-17 — T237 local stack (Sprint 1, in review)

### Added
- `infra/local/compose.yaml`: PostgreSQL 16 with pgvector, Redpanda (Kafka API and schema registry), Redis, SeaweedFS (S3 API), Keycloak with the development realm `kuizi`, MLflow, and LiteLLM as an optional profile. Every service has a health check.
- `Makefile` (`make up`, `smoke`, `status`, `down`, `reset`, `up-llm`, `ml-setup`, `ml-lab`), `.env.example` with the variable names the cloud will use, `scripts/smoke-test.sh` (10 functional checks).
- `ml/`: the brain's Python environment (uv, Python 3.12, PyTorch on CPU, pyKT, JupyterLab, MLflow client) with its lock file.
- `docs/dev/local-setup.md`: setup guide for Windows 11 with WSL2, macOS and Ubuntu.

### Changed
- T237 text: SeaweedFS replaces MinIO, which stopped publishing community images in 2025; LiteLLM is an optional profile (its image is about 1.7 GB). ADR 0006 updated to match.
- Local S3 keys are `S3_ACCESS_KEY_ID` and `S3_SECRET_ACCESS_KEY`, not `AWS_*`, so AWS keys already in a developer's shell never leak into the local stack; in the cloud, services use IAM roles.

### Jira sync
- KK-257 moved to *Revue en cours*, its description updated, and a comment lists what was built and tested.

## 2026-10-17 — Local-first plan: build on the PC, learn the brain early, cloud before the pilot

The product owner works on their own PC, so the five sprints of AWS foundations at the start no longer made sense ([ADR 0006](docs/architecture/decisions/0006-local-first-development.md)). Totals: 240 tickets, 1,636 points, 440 links. The pilot stays in S12 and go-live in S18; S17 is left almost empty as a buffer.

### Added
- T237 (S1) local development stack on the PC: PostgreSQL with pgvector, Kafka (Redpanda), Redis, MinIO, Keycloak, MLflow, LiteLLM and the Python ML environment.
- T238 (S1) brain walkthrough: each Neural Core concept explained simply, with notebooks on public data and an English–Arabic glossary.
- T239 (S14) re-run of the knowledge-tracing benchmark on Kuizi pilot data.
- T240 (S11) move to the cloud: every locally built service goes to AWS staging and production; the pilot (T108) now waits for it.
- `tools/backlog/replan.py`: recomputes the sprint plan (original order as priority, dependencies, capacity ramp, cloud from S8, pilot fixed in S12). Rerun it after the S1–S2 velocity reset.

### Changed
- Sprint 1 is now T237, T234 and T238 (13 points). Cloud tickets (Terraform, VPC, EKS, ArgoCD, Kong, Datadog, Aurora, MSK, Snowflake, MWAA, KMS, Secrets Manager, WAF, CDN, vLLM) move to S8–S11.
- The brain comes earlier: public-data benchmark (T040) in S2, pyKT (T041) in S3, SAINT+ (T042) and the IRT cold start (T043) in S4. The app shell (T076) moves to S3.
- 12 tickets start from the local stack instead of waiting for cloud infrastructure (T006, T012, T023, T025, T026, T027, T032, T041, T059, T061, T092, T134); T040 starts from T238 on public data, and the judge (T062) starts with hosted models through LiteLLM (T059) instead of the self-hosted model (T060). Each carries a "Local-first (ADR 0006)" change line.
- 144 tickets change sprint; phase labels follow the sprint.
- The generator applies `LOCAL_FIRST_SWAPS` and `REPLAN_SPRINTS` from `additions.py`.

### Jira sync
- Created KK-257 to KK-260 (T237–T240) with labels, assignee, estimate and sprint, and added 31 "Blocks" links.
- Moved 143 tickets to their new sprints; regenerated labels and descriptions for 147 tickets and the descriptions of 17 epics; updated 17 sprint goals. Checked: 240 tickets, and every ticket's sprint matches its `sprint-NN` label.

### Pending Jira sync
- Remove 17 obsolete "Blocks" links by hand (the connector cannot delete links). In each ticket, open *Linked work items* and remove the link: KK-21 blocks KK-26 · KK-23 blocks KK-32 · KK-23 blocks KK-79 · KK-25 blocks KK-45 · KK-35 blocks KK-154 · KK-36 blocks KK-79 · KK-41 blocks KK-43 · KK-41 blocks KK-46 · KK-41 blocks KK-47 · KK-48 blocks KK-60 · KK-80 blocks KK-82 · KK-231 blocks KK-32 · KK-231 blocks KK-52 · KK-231 blocks KK-81 · KK-231 blocks KK-112 · KK-237 blocks KK-47 · KK-238 blocks KK-61. Each ticket's description already lists the correct blockers.

## 2026-10-17 — Delivery by role agents, no human team

Kuizi is built by one product owner working with a role-specific AI agent on every ticket ([ADR 0005](docs/architecture/decisions/0005-role-agents-and-one-product-owner.md)). The backlog now speaks of agent roles instead of teams. Totals: 236 tickets, 1,613 points, 426 links; Sprint 1 carries 13 points.

### Changed
- The 14 teams become agent roles. Label `team-*` becomes `agent-*`, the "Team" line in descriptions becomes "Agent role", and the generated backlog's team and headcount table becomes the agent roster with each role's scope.
- No hiring: the staffing lines in ADR 0002, ADR 0004 and the open decisions in the accessibility requirements are superseded. Decisions owned by a CTO, ML lead or engineering manager now belong to the product owner.
- Sprint capacity: the 134-point ceiling stays as the planning limit and is reset from the velocity measured in Sprints 1 and 2.
- T234 becomes the agent operating model (role briefs, Definition of Ready and Done, review gates, least-privilege access, no real student data), 2 → 3 points.
- Sign-offs that named people who do not exist: T215 is reviewed by the product owner and the DPO; T017 and T051 gain a change line naming the product owner, the external DPO and a Tunisian Physics teacher.
- ADR 0005 lists where people outside the project are still needed: legal and DPO sign-off, accessibility testing with students, teacher review of content, pilot schools.

### Jira sync
- Project renamed to **Kuizi Adaptive Bac Platform** (key `KK`).
- All 236 tickets: labels `agent-*` instead of `team-*`, assignee set to the product owner, descriptions regenerated with the "Agent role" line. KK-254 (T234) also gets its new summary and 3 points.

## 2026-10-17 — Sprints and estimates in Jira

No backlog change; Jira catches up with the plan.

### Jira sync
- Backlog and Sprints were turned on in `KK`. Created `APL Sprint 1` to `APL Sprint 20` (Jira sprint IDs 440–459), two weeks each from 2026-11-02 to 2027-08-06, with a goal naming the phase and the main epics.
- Put all 236 tickets in their sprints, matching the `sprint-NN` labels and the generated backlog. No ticket is left outside a sprint.
- Estimation turned on: all 236 tickets carry their story-point estimate (1,612 points in total) and board 37 now estimates by story points.
- Sprint table added to `docs/backlog/README.md`.

### Pending Jira sync
- Project rename from `Kuizi_KPI` to `Kuizi Adaptive Bac Platform` (manual, key stays `KK`). *Done the same day.*

## 2026-10-16 — Gap review: what the final version still needed

The backlog was checked against what a production app for minors needs end to end. 26 tickets were added (T211–T236, 116 points), bringing it to 236 tickets, 1,612 points and 426 dependency links. Every sprint stays at or below 134 points.

### Added
- Foundations nobody had ticketed: Aurora PostgreSQL with pgvector (T211), domains, certificates and email sending (T212), CDN and media store (T213), backend service template and API versioning (T214), Snowflake provisioning with PII masking (T217), Airflow and MLflow (T218), synthetic test data (T219).
- Core learning loop: one item player for every item type (T220) and a server-side answer evaluation service (T221) that feeds knowledge tracing.
- Child safety: a safeguarding policy with a designated lead (T222) and a tutor safety layer that detects distress, abuse and off-topic requests (T223).
- Security and legal: threat model, static analysis and dependency updates (T215), data breach response plan (T216), DPAs with LLM providers and other sub-processors (T236).
- Teachers and schools: classes and join codes (T224), assignments (T225), student profile page (T226), class announcements (T227), school admin management of teachers, classes and seats (T228).
- Mobile: native push and deep links (T229), crash reporting, performance monitoring and device-farm UI tests (T230).
- Brand identity (T231), UI string localisation workflow (T232), ways of working (T234), content production operations (T235), and the yearly Bac session update after go-live (T233).

### Changed
- T185 mock Bac: tutor, hints and the concept map are switched off during a graded paper.
- T108 pilot now waits for T223 and T236; T110 go-live also needs T216.
- Generator: new tickets in the original epics take their phase from their sprint, with the full phase name.

### Jira sync
- Created KK-231 to KK-256, added 75 "Blocks" links, and updated the descriptions of 49 tickets and 13 epics (dependency lines, criteria, scope counts). Jira shows 236 tickets.

## 2026-10-16 — Backlog v2 and project foundation

### Added
- Repository structure: `CLAUDE.md`, `README.md`, `docs/` (product, requirements, architecture, design, backlog), decision records 0001–0004.
- Backlog v2: 20 epics, 210 tickets, 1,496 points, 351 dependency links, generated from `tools/backlog/additions.py`.
  - E14 Inclusive Learning & Accessibility (19 tickets, 134 pts)
  - E15 Focus Mode & Smart Notifications (11 tickets, 54 pts)
  - E16 Native Apps & Store Compliance (12 tickets, 78 pts)
  - E17 Learner Experience & Cyanotype Design System (11 tickets, 68 pts)
  - E18 Bac Simulation, Annales & Grade Prediction (7 tickets, 40 pts)
  - E19 Product Analytics, Growth & Go-to-Market (10 tickets, 45 pts)
  - E20 Support, Back-office & Legal (8 tickets, 36 pts)
- Six new team roles: Mobile, Accessibility, Design / UX, Growth & Marketing, Customer Success & Support, Legal / DPO; `team-*` and `persona-*` labels on every ticket.
- Neural Core traceability (`docs/architecture/neural-core.md`) and the infographic.
- Bilingual concepts brief (EN + AR) in `docs/deliverables/`.

### Changed
- 23 v1 tickets gain acceptance criteria for accessibility, Focus and notifications (listed in `additions.py`, `CHANGES`).
- T085 moves from S13 to S11 and becomes two verification audits (S11, S15).
- T110 go-live also requires T150 (accessibility gate), T207 (legal documents) and T169 (store compliance).
- T142 and T143 placed in S12 to keep S11 within the 134-point capacity.

### Jira sync
- The planned project `APL` was not visible to the connector, so the backlog is mirrored in the existing project `KK` (board 37) instead.
- Loaded into `KK`: 20 epics (KK-1 to KK-20), 210 tickets (KK-21 to KK-230) under their epics, and 351 "Blocks" links. Labels carry the backlog ID, team, persona, phase and sprint.
- The Neural Core infographic is attached to E05 (KK-5).
- `docs/backlog/jira_keys.csv` maps each backlog ID to its Jira key. The generator now prints Jira keys in `APL_Full_Backlog.md` and `apl_backlog.json`, and flags any item missing from Jira.

### Pending Jira sync
- Sprints `APL Sprint 1`–`20`, sprint assignment and story-point estimates. These wait for the Sprints feature on `KK` (Project settings → Features → Sprints). Until then, each ticket's description carries a "Story points" line and a `sprint-NN` label. *Sprints and assignment done on 2026-10-17; estimates still pending, see that entry.*
- Project rename from `Kuizi_KPI` to `Kuizi Adaptive Bac Platform` (manual, key stays `KK`).
