# 0005. Delivery by role-specific AI agents with one product owner

- Status: Accepted
- Date: 2026-10-17

## Context

The backlog was written for a human delivery team: 14 teams, headcounts per team, four engineers to hire (ADR 0002, ADR 0004, the staffing decision in the accessibility requirements) and sprint capacity counted in engineer points. Kuizi has no such team. One person, the product owner, builds it with an AI agent specialised in the role each ticket needs.

## Decision

- Every ticket keeps one owning role, now an **agent role**: Platform / DevOps, Backend, Frontend, ML Engineering, LLM / Applied AI, Data Engineering, QA / SDET, Product + Curriculum, Mobile, Accessibility, Design / UX, Growth & Marketing, Customer Success & Support, Legal / DPO. Jira label `agent-*` replaces `team-*`.
- The product owner is the Jira assignee on every ticket. They brief the agent, review its work and accept it against the acceptance criteria. Nothing merges to `main`, reaches production, goes in front of students or touches minors' data without the product owner's approval.
- Each agent role gets a written brief (scope, tools, environments it may use, hand-off rules) as part of the ways-of-working ticket T234 in Sprint 1. Agents work with least-privilege credentials and never with real student data; development and tests use synthetic data (T219).
- No hiring. The staffing lines in ADR 0002, ADR 0004 and the requirements' open decisions no longer apply.

## Where people outside the project are still needed

Agents prepare the work; some acceptance needs a qualified person:

- Legal and data protection: counsel or an external DPO signs the DPIA, the INPDP declaration (T017) and the legal documents (T207), and confirms the Law 2004-63 rules for minors.
- Accessibility: co-design and screen-reader testing with real students (E14) cannot be replaced by agents.
- Curriculum: Tunisian subject teachers review the knowledge graph and items before students see them.
- Pilot: schools, teachers and parents for the pilot (T108).

## Consequences

- The sprint plan keeps the 134-point ceiling as its planning limit. The real limit is how much the product owner can brief, review and accept in two weeks. Velocity measured in Sprints 1 and 2 resets the ceiling, and the plan is rebalanced then.
- T234 (Sprint 1) becomes the agent operating model: role briefs, Definition of Ready and Done, review gates. It grows from 2 to 3 points.
- The generated backlog shows agent roles instead of teams and headcounts.
