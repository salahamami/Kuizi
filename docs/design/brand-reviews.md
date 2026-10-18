# Brand reviews (T231)

Two acceptance criteria of T231 need people outside the project, so the agent cannot close them. This page holds both briefs and their results. The [brand guide](brand-guide.md) stays **draft** until both are complete and the product owner has accepted the outcome.

| Review | Acceptance criterion | Status |
| --- | --- | --- |
| A. Arabic logotype by a native Arabic type designer | AC2 | Not started: reviewer to be chosen by the product owner |
| B. Trademark availability of the name and the mark | AC3 | Not started: free screening can start now; paid search or counsel needs the product owner's approval |

Both reviews may involve paid services (a type designer's fee, an INNORPI search, an IP attorney). Under the working agreement, the product owner approves any spending and any new vendor first.

---

## A. Arabic logotype review (AC2)

### Who

A native Arabic reader who designs Arabic typefaces or lettering professionally, ideally familiar with Kufic and Maghrebi traditions and with screen typography. One reviewer is enough; a second opinion from a Tunisian reader aged 17–19 is welcome but does not replace the type designer.

### What to send

- `brand/logo/kuizi-wordmark-arabic.svg` and `brand/logo/kuizi-wordmarks-construction.svg` (metrics shared with the Latin logotype)
- `brand/logo/kuizi-lockup-arabic-{light,dark}.svg` and `brand/logo/kuizi-lockup-bilingual-light.svg`
- PNG renders of the Arabic lockup with the star at 24, 32, 48 and 96 px, on tracing-paper `#F3F6FA` and on night `#0B1E3A` (from `brand/export.json` and its `previews`)
- Section 5 of the brand guide (construction and the reasons behind each letter)

### What to check

| # | Question | Pass when |
| --- | --- | --- |
| A1 | Does the logotype read **كويزي** at first sight, without the Latin name next to it? | Unprompted readers read it correctly |
| A2 | Joining: kaf to waw joined; waw not joined to the left; ya to zay joined; zay not joined to the left; final ya isolated | Every join and break is correct |
| A3 | Letter forms: initial kaf (stem with head bar leaning left), final waw, initial ya (tooth), final zay (ra shape), isolated ya (head, side, bowl, upturn) | Each form is the right contextual form and is not mistaken for another letter (for example ya for alif maqsura, waw for the digit ٩, kaf for lam) |
| A4 | Proportions: tooth height against kaf height; waw head size and counter; tail lengths and the 45° angle; length of the baseline joins | Harmonious and in line with Kufic practice |
| A5 | Dots (rhombic nuqta): size against the stroke; ya dots under the tooth; the dots of the final ya inside the bowl rather than below it; the zay dot | Placement is acceptable, or a correction is given |
| A6 | Spacing between the three units, especially the waw tail beside the ya dots and the zay tail beside the final ya | Even rhythm, no collision, no false join |
| A7 | Style: is "geometric Kufi" (naskh structure on a 0/45/90° grid) coherent, or should the logotype move nearer to square Kufic or to naskh? | Clear recommendation |
| A8 | Harmony with the Latin **kuizi** in the bilingual lockup: weight, size, shared baseline | Neither script looks secondary |
| A9 | Legibility at small sizes: waw counter, dots and teeth at 24 and 32 px | Readable at the minimum sizes in section 7 of the guide, or new minimums are proposed |
| A10 | Cultural reading: does the star with its rhombus counter read as a religious marker (۞) or carry an unwanted meaning? | No unwanted reading |
| A11 | The spelling «كويزي» for the brand name | Confirmed, or an alternative is proposed |

### What we need back

A short written review covering each item (pass or change), redlines or corrected vectors for any change, a final sign-off sentence, and the reviewer's name and date. After any change, the agent updates the SVGs and the guide, and the reviewer confirms.

### Result

| Date | Reviewer | Outcome | Changes requested | Signed off |
| --- | --- | --- | --- | --- |
| | | | | |

---

## B. Trademark availability (AC3)

### What to clear

| Sign | Type |
| --- | --- |
| KUIZI | Word mark (Latin) |
| كويزي | Word mark (Arabic) |
| The star with the rhombus counter (`brand/mark/kuizi-star-mono.svg`) | Figurative mark, in black and white |
| The bilingual lockup (`brand/logo/kuizi-lockup-bilingual-mono.svg`) | Combined (word and figurative) mark |

**Nice classes:** 9 (downloadable software and mobile apps), 41 (education, tutoring, online educational content, exam preparation) and 42 (software as a service, hosting of educational platforms). Optionally 16 (printed teaching material), if printed products are planned.

**Territories:** Tunisia first. Then the European Union and France (French-speaking market, app stores, possible partners), and Morocco and Algeria if the product expands in the Maghreb.

### Where to search

| Registry or source | What | Cost |
| --- | --- | --- |
| INNORPI (Institut National de la Normalisation et de la Propriété Industrielle, Tunisia) | National trademark register: availability search for the word marks and the figurative mark in classes 9, 41, 42 | Official search service, usually paid: product owner approval |
| WIPO Global Brand Database | Marks from many national offices and international (Madrid) registrations; word search and image search for the star | Free |
| WIPO Madrid Monitor | International registrations designating Tunisia, the EU, Morocco, Algeria | Free |
| EUIPO eSearch and TMview | EU trade marks and the national registers that take part in TMview | Free |
| INPI France (data.inpi.fr) | French marks | Free |
| App Store and Google Play | Apps named Kuizi or similar in education | Free |
| Domain names and social handles | kuizi.tn (Agence Tunisienne d'Internet), kuizi.com, kuizi.app; handles on the main networks | Free to check |

**Similar names to search as well:** KWIZI, QUIZI, QUIZZI, KUIZY, KIZI (a known online games site), QUIZIZZ (a known quiz platform for schools), and كويز. Classes 9 and 41 make phonetic closeness to existing education and games brands the main risk.

**Figurative search:** use the Vienna classification codes for stars with more than five points and for superimposed quadrilaterals or polygons (confirm the exact codes in WIPO's Vienna Classification tool). The eight-point star is a traditional motif used by many marks, so the mark's protection rests on its particular construction (proportions and rhombus counter) and on the word mark. Counsel should say how much protection the figurative mark can get.

### Steps

1. **Free screening** (main session or product owner, no cost): run every free search above and record the results below.
2. **Decision** by the product owner: continue, adjust the mark, or rename (a rename restarts T231).
3. **Official INNORPI search and, if needed, an opinion from a Tunisian industrial-property attorney** (paid: product owner approval).
4. **Filing** (outside T231): national filing at INNORPI, then a Madrid filing if wanted. This needs a new ticket for the backlog.

### Result

| Date | Source | Query (sign, class) | Relevant hits | Risk (low / medium / high) | Notes |
| --- | --- | --- | --- | --- | --- |
| | | | | | |

Conclusion and product owner decision: _pending_.

---

## When both are done

1. Record the results above and apply any changes to `brand/` and the guide.
2. Change the status line of [`brand-guide.md`](brand-guide.md) from DRAFT to Final, with the date.
3. Re-render the PNGs from `brand/export.json` if any SVG changed.
