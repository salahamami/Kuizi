# 0011. Start with 6e–9e and the two concours; the Bac becomes phase 2

- Status: Accepted (decided by the product owner on 2026-10-24)
- Date: 2026-10-24

## Context

The plan was built for Bac students (17–19). The product owner asked why we did not start with 6e and 9e, which have smaller programmes and an exam families already pay to prepare for, and decided to start there. Three studies support the re-plan:
- `docs/curriculum/college-6-9-scope.md` (subjects, language of instruction, both concours);
- `docs/product/market-6-9.md` (market, prices, competitors, calendar);
- `docs/requirements/minors-11-15.md` (rules for 11–15-year-olds, draft for counsel).

Key facts from them:
- In 6e and collège every subject is taught in Arabic, maths and sciences included.
- The **Sixième** (entry to the collèges pilotes) examines Arabic, French, maths, *éveil scientifique* and English, all with coefficient 1. It takes place on 21–23 June 2027, with about 62,000 candidates.
- The **Neuvième** (the end-of-basic-education diploma, the route into the lycées pilotes) examines Arabic (coefficient 2), maths (2), SVT (2), French (1) and English (1). It takes place on 17–19 June 2027, with about 32,000 candidates. Physical sciences are examined in neither concours.
- Families decide in October–November. The Ministry runs free platforms, and Taki Academy is the main private competitor.
- Law 2004-63 art. 28 requires the guardian's consent and the family judge's authorisation to process a child's data. This applies to every minor, including the Bac students of the previous plan, and needs counsel's opinion before any pilot.

## Decision

1. **Audience:** pupils of 6e année and 7e, 8e and 9e année de base (about 11–15), in age bands A (11–12) and B (13–15) with the rules of `minors-11-15.md`. The two concours are the main buying moments, and Kuizi supports the whole year from 6e to 9e.
2. **Subjects:** all concours subjects: Arabic, French, English, maths, *éveil scientifique* (6e) and SVT (7e–9e). Content order: maths first (both exams, top weight, auto-graded), then sciences, Arabic, French and English. Arabic is the authoritative language for maths and sciences, with French alongside.
3. **Calendar:**
   - a free pilot with a few private schools from February to June 2027, so pupils use Kuizi before the 2027 concours;
   - a paid launch for the 2027–28 school year in September 2027.
   The plan grows from 20 to 24 sprints.
4. **The Bac becomes phase 2**, after the paid launch. Bac-only tickets stay in the backlog without a sprint (label `phase-bac`). The Physics Bac concept graph already built (T032) and the brain work stay.
5. **Design first, with the product owner:** user research, an experience vision, journeys and prototypes tested with children come before any screen is built. No interface code before the product owner confirms the design and the flow (the design gate in `docs/process/working-agreement.md`). The design-ux agent works as a senior product designer, and hiring a human senior designer is recommended.

## Consequences

- **What stays:** the platform and brain work (CI, identity, event schemas, concept-graph store, knowledge tracing, routing, tutor safety, accessibility, offline use, portals, billing).
- **Content work is re-scoped:** concept graphs, item banks, textbook corpora and mock exams move from the Bac to 6e–9e, Arabic first. The physics simulations matter less, and *éveil scientifique* and SVT interactives matter more.
- **Writing in Arabic and French** (the Neuvième essay, the Sixième short writing task) needs rubric-based marking with teacher review. That is new tutor and judge work.
- **New work:**
  - the age-band rules (guided tutor for band A, nicknames, help button, telemetry by band);
  - counsel's opinion on art. 28 and art. 52;
  - a data-residency decision;
  - UX research and a design system v2;
  - concours mock exams and score estimates in place of the Bac versions.
- **Biggest risks:**
  - the legal route for children's data (it may change the consent flow or the pilot);
  - the free Ministry platforms;
  - content volume in five subjects for the September 2027 launch.
