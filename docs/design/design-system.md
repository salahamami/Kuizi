# Cyanotype design system

Cyanotype is Kuizi's visual language: an engineer's technical drawing (blueprint navy, dimension lines, circuit-trace concept maps) with the Tunisian eight-point star as signature. It is implemented in code by T174 and extended for accessibility by T133.

**Design canvas** (all screens, clickable in Play mode): https://claude.ai/artifact/QQuDDhSGx24T1LW3Kn43wi — page "Kuizi — Application".

**Brand** (logo, eight-point star mark, app icons, illustration style, voice and tone in FR and AR): [`brand-guide.md`](brand-guide.md), with source files in [`../../brand/`](../../brand/README.md). The guide is a draft until the reviews in [`brand-reviews.md`](brand-reviews.md) are done (T231).

## Colour tokens

| Token | Hex | Role |
| --- | --- | --- |
| `night` | `#0B1E3A` | Structure, navigation, blueprint surfaces, primary text |
| `tracing-paper` | `#F3F6FA` | Study background |
| `cyan` | `#0A6F8C` | Primary action (white text 5.7:1) |
| `cyan-light` | `#4FD1F0` | Lines and text on night |
| `amber` | `#F5A524` | Current step, remediation (night text on amber) |
| `amber-ink` | `#8A4B00` | Amber text on light backgrounds |
| `coral` | `#C73A30` / text `#9F2A21` | Risk of failure, always with an icon |
| `mint` | `#177A5A` / text `#12704F` | Mastered, always with an icon |
| `ink-2` | `#4A5B75` | Secondary text |
| `line` | `#DCE4EE` | Borders |

Mastery scale (one hue, light to dark, for the teacher heatmap and the concept map): `#E6F1F7`, `#B5D7E8`, `#6FB0CF`, `#2A76A0`, `#0E4E78` for 0–20, 20–40, 40–60, 60–80, 80–100 %.

## Typography

| Use | Typeface |
| --- | --- |
| Titles | Unbounded 700 / 800 |
| Text | IBM Plex Sans 400–700 |
| Labels, data, IDs | IBM Plex Mono 500 |
| Arabic | IBM Plex Sans Arabic 400–700 |
| Reading aids (comfort profile) | Lexend, Atkinson Hyperlegible |

## Components

Buttons (primary cyan, secondary outlined night, remediation amber), mono chips for concept IDs, status chips with icon (at risk, mastered, current step), confidence scale 1–5, hint ladder (question → hint → worked step → locked solution), concept-state nodes (not seen, in progress, at risk, mastered, current), Bac countdown ruler, eight-point star badges.

## Accessibility rules

- Every state carries a shape or icon, never colour alone.
- Focus ring 3 px amber with 2 px offset on every interactive element.
- Touch targets at least 44 × 44 px; text 4.5:1, UI parts 3:1, high-contrast theme 7:1.
- Layouts use CSS logical properties so Arabic mirrors automatically.
- Motion respects `prefers-reduced-motion`; nothing flashes more than 3 times per second.
- Full rules: [`../requirements/accessibility-focus-notifications.md`](../requirements/accessibility-focus-notifications.md).

## Screens on the canvas

| # | Screen | Built by |
| --- | --- | --- |
| 00 | Foundations (this system) | T174, T133 |
| 01 | Sign-up: Bac section, parental consent, placement | T175 |
| 02 | Today: daily plan, Bac countdown, at-risk concepts | T176 |
| 03 | Concept map with remediation route and explanations | T177 |
| 04 | Lab: simulation, confidence, Socratic tutor | T178 |
| 05 | Diagnosis and 1-minute micro-remediation | T179 |
| 06 | Live duel | T181 |
| 07 | Progress, leaderboard by gain, certificates | T180 |
| 08 | Teacher space: class heatmap and alerts | T095, T146 |
| 09 | Parent space in Arabic (right to left) | T097, T160 |

Page **"Version finale"** of the canvas holds screens redrawn as they will ship: Cyanotype tokens, the T231 brand, components as the proposed kits build them (shadcn/ui on Radix and Tailwind for the web, React Aria for complex widgets), working French and Arabic (right to left). First screen: **04 · Labo** on web (live pendulum simulation, answer choices, confidence 1–5, tutor hint ladder) and on phone (Arabic, tutor as a bottom sheet).
