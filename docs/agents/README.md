# Agent roles

Kuizi has no human delivery team: each ticket is done by the AI agent of its role, with the product owner, who approves every change ([ADR 0005](../architecture/decisions/0005-role-agents-and-one-product-owner.md)). Each role has a brief in [`.claude/agents/`](../../.claude/agents/): its mission, what it owns, its tools, what "done" means for it, what it must never do, and the ground rules every agent shares. Claude Code loads these files as project agents, so a session can hand a ticket to the right role by name.

How the product owner and the agents work together (Definition of Ready and Done, review gates, branches, sprint rhythm) is in the [working agreement](../process/working-agreement.md).

| Agent (name) | Jira label | Owns | Tools | Brief |
| --- | --- | --- | --- | --- |
| `platform-devops` | `agent-platform-devops` | Local stack, CI, AWS foundations from S8, move to the cloud | files, shell | [brief](../../.claude/agents/platform-devops.md) |
| `backend` | `agent-backend` | Identity, consent, authorisation, tenancy, portals, notifications | files, shell | [brief](../../.claude/agents/backend.md) |
| `ml-engineering` | `agent-ml-engineering` | The brain: knowledge tracing, benchmark, serving, routing, fairness | files, shell, notebooks | [brief](../../.claude/agents/ml-engineering.md) |
| `llm-applied-ai` | `agent-llm-applied-ai` | LLM gateway, curriculum RAG, judge, tutor safety | files, shell, web fetch | [brief](../../.claude/agents/llm-applied-ai.md) |
| `frontend` | `agent-frontend` | Web app, Cyanotype in code, simulations, item player, FR/AR | files, shell | [brief](../../.claude/agents/frontend.md) |
| `data-engineering` | `agent-data-engineering` | Events, telemetry, warehouse, data quality, synthetic data | files, shell | [brief](../../.claude/agents/data-engineering.md) |
| `qa-sdet` | `agent-qa-sdet` | Working agreement, test suites, load tests, release gates | files, shell | [brief](../../.claude/agents/qa-sdet.md) |
| `product-curriculum` | `agent-product-curriculum` | Concept graphs, items, content operations, subject expansion | files, web research | [brief](../../.claude/agents/product-curriculum.md) |
| `mobile` | `agent-mobile` | Native iOS and Android apps, store compliance | files, shell | [brief](../../.claude/agents/mobile.md) |
| `accessibility` | `agent-accessibility` | Accessibility baseline, screen-reader journeys, audits, gate | files, shell | [brief](../../.claude/agents/accessibility.md) |
| `design-ux` | `agent-design-ux` | Senior product designer: research, experience vision, journeys, prototypes tested with children, Cyanotype craft, brand and content design | files, shell (renders and screenshots its work), web | [brief](../../.claude/agents/design-ux.md) |
| `growth-marketing` | `agent-growth-marketing` | Marketing site, lifecycle messages, store listings, launch | files, web research | [brief](../../.claude/agents/growth-marketing.md) |
| `customer-success-support` | `agent-customer-success-support` | Help center, support desk, teacher and school training | files | [brief](../../.claude/agents/customer-success-support.md) |
| `legal-dpo` | `agent-legal-dpo` | Drafts of legal and privacy documents (signed by counsel) | files, web research | [brief](../../.claude/agents/legal-dpo.md) |

## Least privilege

- **Tools:** each agent gets only the tools its role needs (the `tools:` line of its brief). Document roles cannot run shell commands; no agent has Jira or GitHub settings tools; the main session keeps the backlog and Jira in sync.
- **Credentials:** agents work on the local stack with the local values in `.env`; there are no cloud credentials before the move to the cloud (T240), and then each service gets its own role, not a shared key.
- **Data:** only synthetic or public data; no agent can reach real student data, which does not exist on any PC and, in the cloud, sits behind row-level security and separate keys (T092, T151).

## People outside the project

Agents prepare the work; some acceptance needs a qualified person (ADR 0005): counsel or an external DPO for legal documents, real students for accessibility testing, Tunisian subject teachers for curriculum content, and pilot schools.
