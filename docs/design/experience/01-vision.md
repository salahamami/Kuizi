# Kuizi experience vision (design step 1: kickoff)

| | |
| --- | --- |
| Status | **Draft for the product owner to react to and confirm** (design gate, `docs/process/working-agreement.md`). Nothing here is approved; nothing here is shown to children yet. |
| Date | 2026-10-24 |
| Author | Design / UX agent (senior product designer) |
| Scope | Pupils of 6e année and 7e–9e année de base (about 11–15), their parents and teachers; the Sixième (21–23 June 2027) and the Neuvième (17–19 June 2027) as the key moments; all concours subjects |
| Built on | `docs/product/market-6-9.md`, `docs/curriculum/college-6-9-scope.md`, `docs/requirements/minors-11-15.md` (MR-* rules), `docs/requirements/accessibility-focus-notifications.md`, `docs/design/design-system.md`, `docs/design/brand-guide.md` |

**How to read this kickoff (20 minutes).** This page (5 min) → [`02-journeys.md`](02-journeys.md) (7 min) → open [`03-directions.html`](03-directions.html) in a browser (5 min) → skim [`04-research-kit.md`](04-research-kit.md) (3 min). Then answer the questions at the end of this page.

**Honest framing.** There is no research with Tunisian children, parents or teachers yet. Everything about people below is an **assumption to validate**; [`04-research-kit.md`](04-research-kit.md) is the plan to validate it. The design is built so that the riskiest assumptions are tested first.

## 1. The vision, in one paragraph a parent would understand

> Kuizi is a calm coach on the family phone. Every evening it gives your child one short mission, about fifteen to twenty minutes, chosen from what your child already knows and what comes next, in the subjects of the Sixième or the Neuvième. Maths and science are in Arabic, as at school, with French alongside. When your child is stuck, Kuizi explains in one minute instead of giving the answer. It celebrates effort, never compares children and never puts on pressure. Once a week you see, in ten seconds, what your child practised, what is getting stronger and how you can help.

The same paragraph as product copy, to test with parents (Arabic **for native review**):

- FR : « Kuizi, c'est un coach calme sur le téléphone de la famille. Chaque soir, il propose à votre enfant une seule mission courte, de quinze à vingt minutes, choisie selon ce qu'il sait déjà et ce qui vient ensuite, dans les matières de la Sixième ou de la Neuvième. Les maths et les sciences sont en arabe, comme à l'école, avec le français à côté. Quand votre enfant bloque, Kuizi explique en une minute au lieu de donner la réponse. Il valorise l'effort, ne compare jamais les enfants et ne met pas de pression. Chaque semaine, vous voyez en dix secondes ce que votre enfant a travaillé, ce qui progresse et comment l'aider. »

<div dir="rtl" lang="ar">

- AR: «كويزي مرافق هادئ على هاتف العائلة. كلّ مساء، يقترح على طفلكم مهمّة واحدة قصيرة، من خمس عشرة إلى عشرين دقيقة، يختارها حسب ما يعرفه وما يأتي بعده، في موادّ السيزيام أو النوفيام. الرياضيات والعلوم بالعربية كما في المدرسة، مع الفرنسية إلى جانبها. وعندما يتعثّر طفلكم، يشرح كويزي في دقيقة واحدة بدل إعطاء الجواب. يثمّن المجهود، ولا يقارن الأطفال ببعضهم أبدًا، ولا يضغط عليهم. وكلّ أسبوع، ترون في عشر ثوانٍ ما تدرّب عليه طفلكم، وما يتحسّن، وكيف يمكنكم مساعدته.»

</div>

## 2. Principles

Seven principles. Every design proposal names the ones it serves; when two conflict, the order below decides.

| # | Principle | This means | This does not mean |
| --- | --- | --- | --- |
| 1 | **Safe and honest first.** The age-band rules are design material, not a compliance layer. | Parents set up the account and hold the controls for band A (MR-F1). The child sees what parents and teachers see (MR-F3). "J'ai besoin d'aide" is on every pupil screen (MR-G2). We never promise admission. | Dark patterns presented as "engagement". A predicted concours grade for an 11-year-old (MR-P3). Purchase prompts to pupils (MR-M3). |
| 2 | **One next step.** A coach, not a dashboard. | "Today" shows one mission and one button. Kuizi chooses the order; the pupil may pick another subject. Every screen has one primary action. | A home page of widgets, charts and badges. A catalogue to browse before doing anything. |
| 3 | **Calm by default.** | Weekly goals that never reset to zero (MR-S5). The concours shown as a plan of weeks, not a ticking day counter (MR-S9). At the end of a session the primary action is "stop for tonight". At most one message a day; quiet hours. | Streaks or flames for 11–12. "Plus que 12 jours !". Red alarms. "Encore un ?" loops. Timers outside exam practice. |
| 4 | **Effort you can see.** Progress you can feel. | Progress against the pupil's own past ("3 notions are now solid"). Every session closes with a small, true win. Mistakes are part of learning: Kuizi never uses the teacher's red pen. | Percentages and failure probabilities (MR-P3). Red crosses. Comparison with other children (MR-S1, MR-S2). |
| 5 | **Arabic first, French equal.** | Maths and science in Arabic, as taught up to 9e (Law 2002-80, art. 24), with the French term one tap away as the bridge to lycée. The interface mirrors fully. Numbers, formulas and units stay left to right. Each script has its own face and size. | A French product translated into Arabic. Mirrored formulas. Arabic squeezed into a Latin font, or letter-spaced. |
| 6 | **Parents in ten seconds.** | One sentence, three facts (effort, what is getting stronger, what to work on) and one thing to do at dinner. Weekly, in the language the parent chooses. | Item-by-item logs, timelines of home use (MR-E3), rankings. A surveillance feed of a 14-year-old (MR-F2). |
| 7 | **Grows up with the child, works on every phone.** | Band A: more guidance, pictures, audio, guided help buttons (MR-T1). Band B: denser screens, more choice, a teenager's tone. The structure stays the same from 6e to 9e. WCAG 2.2 AA, 44 px targets, screen readers in both languages, 2 GB Android, offline sessions, little data, a shared parent phone. | A cartoon theme a 15-year-old is embarrassed by. One tone for everyone. Video-first lessons that eat a prepaid data plan. Accessibility "later". |

## 3. Proto-personas (assumptions to validate)

Synthetic people, built from the market study, the curriculum study and the legal draft. **Every line is an assumption** until the research in `04-research-kit.md` confirms or replaces it.

### Lina, 11, 6e (band A)

- Public primary school in Ben Arous. Registered for the Sixième in November because her teacher suggested it.
- Uses her mother's Android phone after dinner, on mobile data. No computer at home.
- Comfortable reading Arabic, which is the language of her maths and *éveil scientifique*. French reading is slow and makes her feel "bad at school".
- Hears "the Sixième" at home and at school as the big exam everyone talks about. Afraid of disappointing her parents.
- **Needs:** to know what to do tonight without asking anyone; to feel she is getting better; help when stuck, without feeling stupid.
- **Kuizi must:** give one clear mission, read questions aloud on request, turn mistakes into a one-minute lesson, end on a win, and talk to her parents rather than to her about schedules.

### Adam, 14, 9e (band B)

- Public collège in Sfax. His own Android phone with a prepaid plan.
- Private maths lessons twice a week. Wants a lycée pilote, like his cousin.
- Independent, quick to call anything "for kids". Revises late. Arabic composition and SVT memorisation worry him most.
- **Needs:** an efficient plan, honest feedback, control over what he works on, and privacy about the details.
- **Kuizi must:** respect his time (a plan he can bend), show what is solid and what is not without childish praise, let him ask a question about the exercise (band B, MR-T1), and keep his parents' view to a summary (MR-F2).

### Samia and Hichem, parents

- Samia (41) is a nurse on shifts. She follows schoolwork day to day and reads Arabic most comfortably. Hichem (44), the legal tutor, works away during the week.
- Together they spend about 250 TND a month on private lessons for two children (market study, section 2).
- **Worry:** "Is she on track? Are we paying for the right thing?" They live on WhatsApp and Facebook.
- **Needs:** understand progress in ten seconds and know how to help. Trust: no ads, data kept safe, pay in dinars without a foreign card.
- **Design consequence:** the parent who consents (the legal tutor, art. 28) may not be the parent who follows the child every day. The flow must work for two adults.

### Mme Rim, teacher

- Teaches a 6e class of 28 in a private primary school in Ariana (private schools first, MR-E8).
- Prepares the class for the Sixième, with a mock exam in February. Runs a parents' WhatsApp group.
- Has about ten minutes a week for any new tool, mostly on her phone.
- **Needs:** which notions the class has not got yet, a set she can assign in one tap, no extra admin, no rankings.
- **Design consequence:** she sees notions and counts first, names second, and never home-use timestamps (MR-E3).

## 4. The three moments that matter most

1. **The first evening.** A parent and a child, together, for ten minutes. The parent decides whether to trust Kuizi and the child decides whether it is "for them". It must end with a win and a clear "tomorrow", never with a test verdict. *Risk:* the legal steps (art. 28, art. 31) may turn the first evening into a wait of days or weeks. `02-journeys.md` designs for that.
2. **The moment of being stuck.** 20:40, the second wrong answer on the same notion, tired. This is where children give up, or call a parent and the evening ends in tears. Kuizi must turn it into a one-minute lesson and a success on the next try.
3. **The night before the concours.** The most anxious evening of the year. Kuizi's job is to make it smaller: light review or nothing at all, a practical checklist, sleep. No new notions, no scores.

## 5. What success looks like

First in usability rounds (two rounds of five children per band, then parents and teachers), then in the pilot. Product analytics are aggregate only (MR-D6). Targets are proposals for the product owner.

| Measure | Target (proposal) | How it is measured |
| --- | --- | --- |
| Three-second test: the pupil points to "what to do now" on Today | 9 of 10 pupils in each band | Usability round, first-click test |
| Ten-second test: the parent says what improved and what to work on | 8 of 10 parents | Usability round, summary shown for 10 s |
| First evening: setup to the child's first win in one sitting (once the account is active) | 8 of 10 test families | Usability round |
| Stuck moments resolved: a correct answer on the next similar item after a one-minute lesson | At least 60 % | Aggregate, pilot |
| Weekly goal met | Median pupil meets it in 3 of 4 weeks | Aggregate, pilot |
| Healthy sessions (a guardrail, not a growth target) | Median 12–25 min; at most 5 % of sessions reach the parent's limit | Aggregate, pilot |
| Enjoyment | At least 4 of 5 on a five-face scale | Usability round |
| Calm | Self-rated worry about the concours is not higher after using the concours plan | Research only, paired face scale, with consent. Never inferred from telemetry (MR-D8) |
| Accessibility | 95 % completion of the core journey with screen readers (NFR-3) | Co-design rounds (T150) |
| Zero tolerance | No notification in quiet hours; no shaming copy | Monitor (T161); content review |

We deliberately **do not** measure success by minutes spent in the app, daily active streaks or notification open rates.

## 6. What we will deliberately not do

- No streaks or flames for band A. No leaderboards outside the class. No public profiles (MR-S1, S2, S4, S5).
- No day countdown to the concours on pupils' screens (MR-S9). No predicted grade or admission odds for children (MR-P3). No promise of admission, anywhere.
- No talking mascot and no AI "friend". The tutor says it is an AI and has no persona (MR-T4). No open chat for band A (MR-T1).
- No red crosses, no loss-framed copy, no guilt notifications (FR-N6).
- No ads, no purchase prompts to children, no "your friends have Premium" (MR-M1, M3).
- No rainbow of subject colours, no emoji as interface, no stock photos of children, no photos of minors at all.
- No video-first lessons. The one-minute lesson is interactive and light on data.
- No notifications to band A devices by default, and no re-engagement messages to pupils (MR-N1, N4).
- No surveillance views: no home timestamps for teachers, no item logs or tutor text for parents of band B (MR-E3, MR-F2).

## 7. What changes from the current canvas (Cyanotype v1)

The product owner's critique is right: the v1 canvas reads as a generic SaaS template drawn for 17–19-year-old engineers. Keep what is good, drop the rest.

| Keep | Drop or rethink |
| --- | --- |
| The najma star with its nuqta counter, and the 0/45/90° geometry (brand, T231) | Blueprint navy panels, dimension lines and circuit traces as decoration |
| The accessibility rules: logical properties, 3 px focus ring, 44 px targets, no colour alone | Unbounded titles (no Arabic glyphs, so Arabic always looked second) |
| IBM Plex Sans Arabic as a candidate UI face | IBM Plex Mono labels, concept-ID chips and rows of status chips in pupil screens |
| Mastery as states, not numbers (MR-P3) | Five status hues on one screen (cyan, amber, coral, mint, navy); the mastery % scale in pupil views |
| A calm, precise voice | The "engineer" voice and Bac copy written for 17–19; the Bac countdown ruler |

`03-directions.html` shows three new directions. Whichever is chosen becomes **Cyanotype v2** (renamed if the direction no longer fits the name), and the brand guide's colour and type sections change with it. That is a brand decision for the product owner.

## 8. The product owner's reference: principles, not the look

The product owner named Claude Code and [claude.com/fr/programs/startups](https://claude.com/fr/programs/startups) as "clean, good vision and workflows". I studied the page at 1440 px and 390 px. We take its principles, not its brand: no Anthropic colours, typefaces, mark or illustrations.

| Principle | What the reference does | What it becomes in Kuizi |
| --- | --- | --- |
| Restraint | Warm off-white page, near-black text, secondary text in grey; one accent, kept for the logo | Warm neutrals carry the screen; one brand hue for identity and the single primary action; secondary text by tone |
| Generous whitespace | Sections far apart; hairline rules instead of boxes on the phone | One thing per screen; air and ruled lines instead of cards |
| Editorial hierarchy | Large, light serif headline over a quiet sans; a small kicker above each headline | The mission as a sentence in a display face (a Naskh for Arabic), a kicker such as "Jeudi soir · Maths", the interface in a sans |
| Purposeful illustration | One small monoline drawing per section | One commissioned spot drawing per screen that carries the notion |
| One idea per section | Kicker, headline, one paragraph, one action | One idea per screen: tonight's mission |
| Calm, clear flows | Few calls to action; outlined or text secondary actions | One filled button; text links for alternatives; short motion |

**What we do not take:** the centred hero (Arabic-first screens align to the start edge, and long centred lines are harder for young readers), photography and video of people (no photos of minors, MR-M2; data cost), and headlines that fade in from light grey (the faded words fall below 4.5:1).

**How the directions measure up:** A "Cahier" is the calm, editorial direction built on these principles, adapted to children. B follows restraint and one idea, but adds a second hue, a shadowed card and more shapes. C is furthest: one idea and a clear flow, but a large saturated surface breaks restraint and calm.

## 9. Questions for the product owner (to move to step 2)

Please answer in the ticket or in chat. Short answers are fine.

1. **Vision and principles.** Does the parent paragraph say what you want Kuizi to be? Do you accept the seven principles and their order (safety first, then one next step, then calm)?
2. **Direction.** Which direction in `03-directions.html` do you want to take into step 2: A "Cahier" (my recommendation, and the one built on your reference), B "Ligne", C "Élan", or a mix? What do you dislike in the one you choose? Did section 8 capture what you like in your reference?
3. **Brand colour.** Direction A moves the brand from cyan to ink blue; B keeps cyan; C moves to violet. May the brand colour change, or must it stay cyan?
4. **No countdown.** May we show the concours as "week 3 of 8" in pupil screens, with the exam date only on the parent's side and in exam practice (MR-S9)? Or do you want a day count for band B (13–15) only, as an opt-in?
5. **Practice-paper marks.** In exam-format practice, may band B see a mark out of 20 for the paper, while band A sees only which exercises went well? (A predicted grade stays off for everyone, MR-P3.)
6. **Who joins first.** At launch, band A (6e, most 7e) can join only through a school (MR-C3). Do we design the first run as "school code first" for 6e, with direct sign-up for 8e–9e only, until counsel answers?
7. **Parent channel.** Weekly summary by SMS with a link plus in-app, or do you want WhatsApp explored (a foreign vendor and a transfer abroad, so counsel and your approval are needed)?
8. **Research.** Will you run the research in `04-research-kit.md` yourself, recruit a researcher (a paid service), or should we start with parents and teachers only (no children) while the research protocol (NEW-11) is approved?
9. **Copy decisions** still open from the brand guide (section 16): *tu* for pupils and *vous* for parents; gender-neutral Arabic for pupils; Western digits in Arabic; no derja in product copy. Confirm or change.
10. **Names in copy.** Pupils say «السيزيام» and «النوفيام». May product copy use these everyday names, with the official names in the parent's legal texts?
