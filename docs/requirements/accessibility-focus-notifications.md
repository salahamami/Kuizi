# Requirements: accessibility, Focus mode and smart notifications

Kuizi builds accessibility, Focus mode and smart notifications into the platform from sprint 4, as engineering work with owners and release gates. The tickets live in epics E14 and E15 of [`../backlog/APL_Full_Backlog.md`](../backlog/APL_Full_Backlog.md). The live, commentable version of this document (with the architecture diagram and sprint-load chart) is https://claude.ai/code/artifact/dc047f9e-1e84-4f5f-a3df-382fa67369cc.

**Who it serves.** Students who are blind or have low vision, colour-vision deficiency, hearing loss or limited dexterity; students with dyslexia, dyscalculia, dysgraphia, attention difficulties (ADHD), anxiety, autism or photosensitive epilepsy; students with an official exam accommodation such as extra time; anyone in a temporary situation. Every student gets Focus sessions and notifications that arrive at a useful moment.

**Standard.** WCAG 2.2 level AA on the web, Apple and Android accessibility guidelines on the native apps, EN 301 549 for school procurement. Every capability works in French and in Arabic, right to left included. Defaults below (times, budgets, durations) are proposals the team can tune.

## 1. Functional requirements

### 1.1 Accessibility, by need

| ID | Need | Requirement | Tickets |
| --- | --- | --- | --- |
| FR-A1 | Low vision | Text scales to 200 % without loss; high-contrast theme; Atkinson Hyperlegible font; zoom inside simulations | T133, T140 |
| FR-A2 | Blind, screen reader | The full journey (sign-up, item, hint, tutor, results) works with VoiceOver, TalkBack and NVDA in French and Arabic; feedback announced through live regions | T136 |
| FR-A3 | Blind: maths and simulations | Formulas read correctly (MathML with French and Arabic speech rules); every simulation has a live text description and a sonified mode | T137, T138 |
| FR-A4 | Colour-vision deficiency | No information carried by colour alone: every state also has a shape, icon or label | T133 |
| FR-A5 | Deaf or hard of hearing | Captions and transcripts for all audio and video, the tutor's voice included; visual and haptic alternatives to every sound | T147 |
| FR-A6 | Limited dexterity | Every action works by keyboard, switch access and voice control; no drag-only interaction; touch targets of at least 44 px | T139 |
| FR-A7 | Dyslexia | Lexend or Atkinson font, letter and line spacing, reading ruler, read-aloud with word highlighting | T140, T141 |
| FR-A8 | Dysgraphia | Dictation and the maths keypad replace handwriting wherever a typed answer is expected | T141 |
| FR-A9 | Dyscalculia | Step scaffolds for numeric items and visual quantity aids; calculator allowed outside graded tests | T142 |
| FR-A10 | Attention (ADHD) | One task per screen, items split into steps, short sessions with break prompts, Focus sessions | T142, T155 |
| FR-A11 | Anxiety, autism | Calm mode hides timers, leaderboards and duels; predictable layout; session preview; gentle feedback wording | T143 |
| FR-A12 | Photosensitivity, vestibular | No flashing above 3 times per second; reduced motion honoured; every animation can be paused | T133 |
| FR-A13 | Language and comprehension | Simplified French and Arabic (FALC) variants; key terms shown in both languages | T144 |
| FR-A14 | Exam accommodations | Time multiplier (×1.33, ×1.5, untimed) applies to timed items, duels and the mock Bac; teachers see it only if the student shares it | T145, T146 |
| FR-A15 | Temporary situations | Any setting can be switched on in two taps from any screen, and works offline | T134, T083 |

### 1.2 Comfort profile

- **FR-P1** One profile per student, set during onboarding (optional step) or at any time; presets combine.
- **FR-P2** Applied on every screen and device; follows the operating system by default (text size, reduced motion, screen reader).
- **FR-P3** Private by default; each accommodation is shared with a teacher or parent only when the student chooses to.

### 1.3 Focus mode

- **FR-F1** Focus sessions of 15, 25 or 45 minutes from the daily plan or any exercise.
- **FR-F2** During a session only essential notifications (consent, account security); duel invites and leaderboards hidden; one task at a time.
- **FR-F3** The session turns on the device's own Focus or Do Not Disturb where allowed; Kuizi respects a Focus started from the OS.
- **FR-F4** A break prompt after each session (default 5 minutes after 25), following the comfort profile.
- **FR-F5** End-of-session summary: what was practised, mastery change, next step; stopping early carries no penalty.
- **FR-F6** Sessions logged as `focus.start` / `focus.end` events for the daily plan and the send-time model.

### 1.4 Smart notifications

- **FR-N1** Every notification goes through one Notification Orchestrator; no service sends directly.
- **FR-N2** Priority classes: essential (always delivered), useful (review due, plan reminder, duel invite), optional (off by default).
- **FR-N3** Nothing non-essential during quiet hours (default 22:00–07:00), class hours (tenant timetable) or a Focus session; deferred messages are batched into one digest.
- **FR-N4** Daily budget per student (default 2 useful messages), enforced server-side.
- **FR-N5** Send time chosen per student from study history, inside the allowed windows.
- **FR-N6** Tone: kind, specific, never guilt-based, plain language, screen-reader friendly, never emoji-only.
- **FR-N7** Exam-aware: slightly more reminders in the 4 weeks before the mock Bac and the Bac, none after 21:00 in exam weeks; exam eve is calm review only.
- **FR-N8** Control per category and channel (push, SMS, email); parents get the same quiet hours and budget.
- **FR-N9** Every notification is measured and can be stopped by a global kill-switch.

## 2. Non-functional requirements

| ID | Area | Target | How it is checked |
| --- | --- | --- | --- |
| NFR-1 | Conformance | WCAG 2.2 AA (web), Apple and Android guidelines (native), EN 301 549 | Expert audits S11 and S15; zero open critical issues at go-live |
| NFR-2 | Automated checks | No new critical or serious axe-core violation on any pull request | CI gate (T149) |
| NFR-3 | Screen-reader completion | At least 95 % of the core journey completed by blind students (proposed) | Co-design rounds (T150) |
| NFR-4 | Reflow and zoom | Text at 200 % and 320 px viewport with no horizontal scroll or lost content | Playwright snapshots in FR and AR |
| NFR-5 | Contrast | Text 4.5:1, UI parts 3:1; high-contrast theme 7:1 | Token validator |
| NFR-6 | Targets and motion | Targets at least 44 × 44 px; no flashing above 3 per second; reduced motion honoured | Component tests |
| NFR-7 | Read-aloud latency | First audio under 800 ms at p75 on 3G (proposed) | Real-user monitoring |
| NFR-8 | Dictation quality | Word error rate of at most 20 % on Tunisian Arabic | 100-utterance test set |
| NFR-9 | Profile application | Comfort profile applied before first paint; available offline | E2E and offline tests |
| NFR-10 | Notification discipline | Zero non-essential sends in protected windows; budget never exceeded; decision under 50 ms | Production monitor (T161) |
| NFR-11 | Privacy | Accommodation data under its own KMS key, every read audited, never in rankings, exports or LLM prompts beyond the minimum flag | Security review, audit log |
| NFR-12 | Languages and devices | Every feature works in FR and AR right to left, on 2 GB RAM Android devices | Test matrix (T102, T085) |

## 3. Data protection

An accommodation such as "screen reader" or "extra time" can reveal a disability, so Kuizi treats it as sensitive health-related data under Law 2004-63, on top of the minors' rules in E02.

| Data | Class | Who can see it | Storage and retention |
| --- | --- | --- | --- |
| Comfort settings with no health meaning (font, theme, text size) | Personal | The student | Comfort Profile service, while the account is active |
| Accommodation flags that imply a need | Sensitive | The student; a teacher or parent only for flags the student shares | Separate encrypted schema, own KMS key, every read logged (T022) |
| Official accommodation proof (medical documents) | Not collected | Nobody in Kuizi | The school attests the multiplier; Kuizi stores the multiplier and who attested it |
| Dictation audio | Transient | Nobody | Transcribed then discarded |
| Focus sessions, notification history | Personal | The student; aggregates for the teacher | 24-month telemetry rule (T018) |

Rules the code enforces: separate revocable consent for accommodation data; accommodation data never enters leaderboards, analytics exports, parent summaries or LLM prompts beyond the minimum flag; erasure and export include the comfort profile; the DPIA and privacy notice (FR, AR) cover this processing before the first pilot school.

## 4. Model fairness

Without changes, SAINT+ would read a screen-reader user's listening time or a student's extra time as hesitation. T148 fixes this before the first champion/challenger gate (T047, S9):

1. Normalise elapsed and lag time by the time multiplier; track assistive reading time apart from thinking time.
2. The telemetry SDK emits no `item.hesitation` while assistive audio plays or a voice command runs.
3. An assistive-mode embedding lets the model learn these patterns instead of penalising them.
4. T047 adds fairness slices by accommodation type; promotion is blocked if any slice loses more than 1 AUC point.
5. Small groups are reported with confidence intervals; below a minimum sample size the router leans on the IRT blend.
6. Session length, item splitting and hint timers follow the comfort profile; leaderboards rank mastery gain only.

## 5. Testing and release gates

| Layer | What runs | When | Blocks |
| --- | --- | --- | --- |
| Code | jsx-a11y lint, axe-core component checks | Every commit | Merge |
| Pull request | Playwright a11y suite, 200 % zoom and RTL snapshots (FR, AR) | Every PR | Merge |
| Preview env | pa11y crawl, keyboard-only walk-through | PRs with UI changes | Merge |
| Release | VoiceOver, TalkBack, NVDA smoke flows on the core journey | Every release | Release |
| Expert audit | External WCAG 2.2 AA audit | S11 and S15 | Go-live if critical issues stay open |
| Co-design | 3 rounds with students with disabilities via Tunisian associations, at least 5 per need group | S9, S11, S15 | Go-live if NFR-3 is not met |
| Notifications | Monitor for protected-window sends, opt-outs, complaints | Continuous | Kill-switch (T161) |

**Go-live accessibility gate.** No open critical or serious issue; NFR-3 met; accessibility statement published in AR and FR with a barrier-reporting channel; zero non-essential sends in protected windows during the 14-day pilot.

## 6. Open decisions

| Decision | Recommended default | Owner |
| --- | --- | --- |
| Native learner apps or PWA on iOS | Native SwiftUI learner app; portals stay web (ADR 0004) | Product owner |
| Who sees a minor's accommodations | Student chooses per flag; parents see what is shared; counsel confirms against Law 2004-63 | DPO, legal |
| Proof of official accommodations | No medical document stored; a school admin attests the multiplier | Product |
| Read-aloud voices | Managed cloud voices first for Arabic quality, self-hosted later, monthly cost cap | Product owner |
| Default notification budget | 2 useful messages a day for students, 1 weekly summary for parents | Product |
| Tunisian Sign Language content | Out of scope for v1; revisit with associations after the pilot | Curriculum |
| Staffing | No hires: each ticket is done by the agent of its role with the product owner (ADR 0005) | Product owner |
