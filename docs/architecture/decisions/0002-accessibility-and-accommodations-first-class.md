# 0002. Accessibility and accommodations are first-class platform capabilities

- Status: Accepted
- Date: 2026-10-16

## Context

v1 placed accessibility in a single late ticket (T085, S13). Students with disabilities and students with official exam accommodations would then meet a product designed without them, and the knowledge-tracing model would read assistive use (screen-reader listening, extra time) as hesitation.

## Decision

- Accessibility is built from S4 in the design system (T133, T174) and verified, not built, by audits (T085 in S11 and S15).
- A Learner Comfort Profile service (T134) holds preferences and accommodations for every client.
- Accommodation flags are sensitive health-related data: separate schema, own KMS key, explicit consent (T151).
- SAINT+ normalises time features by the time multiplier and gets an assistive-mode embedding, with fairness slices in the promotion gate (T148, T047).

## Consequences

Epic E14 adds 19 tickets and 134 points. One accessibility engineer joins from S4. Go-live (T110) is blocked by the accessibility gate (T150).
