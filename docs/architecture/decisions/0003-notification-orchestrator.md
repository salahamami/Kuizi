# 0003. One Notification Orchestrator for every message

- Status: Accepted
- Date: 2026-10-16

## Context

Several services (routing, spaced repetition, duels, parent summaries, lifecycle marketing) want to message students. Without a single gate, students get messages during class, at night or while studying, and budgets cannot be enforced.

## Decision

All notifications go through the Notification Orchestrator (T152), which applies priority classes, a daily budget, quiet hours, school timetables, Focus state and exam-week rules, then hands messages to the delivery layer (T089). Network policy prevents direct calls to delivery.

## Consequences

Epic E15 owns the rules; T089 becomes a delivery-only service. Lifecycle marketing (T196) must use the Orchestrator.
