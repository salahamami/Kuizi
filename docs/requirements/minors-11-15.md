# Minors aged 11 to 15: law, design rules and plan changes

> **DRAFT — not legal advice.** Prepared by the Legal / DPO agent on 2026-10-24, to be reviewed by a qualified Tunisian lawyer and Kuizi's external DPO (ADR 0005). Nothing here is final. It must not be shown to schools, parents, authorities or vendors as Kuizi's position until counsel or the DPO signs it. Section 6 lists the open legal questions; they are left for counsel and not answered by assumption.

| | |
| --- | --- |
| Decision it follows | The product owner's decision that Kuizi starts with pupils from 6e année (about 11–12) to 9e année de base (about 14–15), instead of Bac students (17–19) |
| Status | Draft, not reviewed |
| Prepared by | Legal / DPO agent |
| Reviewed and signed by | Pending: counsel, the external DPO, and a child-protection adviser for section 4.12 |
| Relation to other requirements | Adds to [`accessibility-focus-notifications.md`](accessibility-focus-notifications.md) section 3. Where this draft is stricter, the stricter rule applies until the product owner settles the conflicts listed in section 5.4 |
| Rule IDs | `MR-*` rules (section 4) are what tickets cite under the Definition of Ready, point 5 |

**How to read the markers.**

- **[Confirmed]**: read in the text named as the source (section 8).
- **[Unconfirmed]**: comes from a secondary source or from memory, so counsel must check it.
- **[Good practice]**: not binding in Tunisia; Kuizi adopts it as a design rule.
- **[Contract]**: binding through an app store or vendor agreement, not through law.

## 0. At a glance

All of Kuizi's learners are now children. The Child Protection Code defines a child as anyone under 18, and Law 2004-63 gives a child no age at which they can consent to data processing alone. Five consequences follow:

1. **Consent needs two keys, and this blocks launch.** Article 28 of Law 2004-63 allows a child's data to be processed only after **the tutor's consent and the family judge's authorisation** (*juge de la famille*). Breaking it is punishable by 2 years in prison and a 10,000 TND fine (art. 87), and the managers of a company are personally liable (art. 101). The current plan (T013) covers only the parent's consent. How Kuizi meets article 28 is a question for counsel (Q1–Q3). It may be possible through public schools (art. 53–54) or through a judge's authorisation.
2. **Data cannot leave Tunisia without authorisation.** Every transfer abroad needs INPDP authorisation (art. 52). When the data belongs to a child, the request goes to the family judge. This affects AWS Paris (T240), the LLM providers, Snowflake and Datadog. A data-residency ADR is needed before the cloud move (NEW-6).
3. **Features change by age band.**
   - Ages 11–12 (band A): no open chat with the AI tutor, no leaderboards, and no duels except teacher-run class battles. Reminders go to the parent.
   - Ages 13–15 (band B): free text with the tutor, but only about the current exercise. Leaderboards and duels exist only inside the class, under nicknames, and are off until switched on.
   - Neither band has public rankings, chat between pupils, advertising or engagement profiling.
4. **Less data, and profiling only for learning.** Fine-grained behaviour tracking is off for band A, and retention is shorter. Knowledge tracing may only choose exercises; it is never used to decide on orientation, admission, grades or discipline.
5. **Safeguarding is a legal duty.** Article 31 of the Child Protection Code obliges everyone to report certain threats to a child to the *délégué à la protection de l'enfance*. Every pupil gets a "J'ai besoin d'aide" button that shows the helplines (1809).

The plan needs changes to **100 existing tickets** (section 5.2) and **12 new tickets** of about 42 points (section 5.5). Four of the new tickets (NEW-1, NEW-3, NEW-6, NEW-10) must be done before T013, T017, T093 or T240 can close.

## 1. Scope and age bands

**Who is covered.** Pupils of 6e année (the last year of primary school) to 9e année de base (the last year of the preparatory cycle, the *collège*), and their parents or tutors, teachers and school administrators. Pupils who repeated a year can be 16 or 17 in these grades. They stay under the band B rules: every pupil is a child until 18 (Child Protection Code art. 3), and nothing in Law 2004-63 makes 16 or 17 different (Q18).

| Band | Ages | Typical grades | Why the line falls at 13 |
| --- | --- | --- | --- |
| **A** | 11–12 (under 13) | 6e, 7e | Tunisian law itself uses 13 as a threshold for the child's own voice. From 13, a child signs agreements made with the *délégué à la protection de l'enfance* and must be told they can refuse a proposed measure (Child Protection Code art. 40, 42) [Confirmed]. Civil law gives a child limited capacity from 13 [Unconfirmed]. 13 is also the COPPA threshold, the lowest age of digital consent the GDPR allows, and the boundary between two UK Children's Code age ranges (10–12 and 13–15) [Good practice] |
| **B** | 13–15 (and older pupils in these grades) | 8e, 9e | |

The band comes from the birth month and year the parent declares. It is checked against the grade, and it changes on the first day of the month after the 13th birthday (MR-C9).

**Sources.** The full French text of Law 2004-63 was read from the DCAF consolidated copy, and the Child Protection Code from the annotated UNICEF and Ministry edition. Neither is the official Journal officiel (JORT), and the Code edition may predate later amendments. Counsel should check both against the official consolidated texts (Q23).

## 2. Tunisian law

### 2.1 Organic Law 2004-63 of 27 July 2004 on personal data

All articles in this table are **[Confirmed]** in the French text. Quotes are short; the rest is paraphrase.

| Topic | Article | What it says | What it means for Kuizi with 11–15-year-olds |
| --- | --- | --- | --- |
| Prior declaration | 7 | Every processing operation needs a prior declaration to the INPDP. If the INPDP does not object within one month, the processing is accepted. Procedures are set by decree | A declaration is filed before any real pupil data is processed (T017). The procedural decree is Decree 2007-3004 [Unconfirmed title] |
| Authorisation file | 8 | Lists what an authorisation request contains, including a statement that the article 22 conditions are met | Applies to the authorisations in the rows for articles 15, 49 and 52 |
| Principles | 9–12 | Respect for dignity and privacy (9). Lawful, determined and explicit purposes (10). Processing must be fair, limited to what is necessary, and accurate (11). No other purpose without consent, a vital interest or a scientific purpose (12) | Basis for data minimisation (MR-D) and the learning-only purpose (MR-P1) |
| Sensitive data | 14, 15 | Processing data that reveals racial or genetic origin, religion, opinions or **health** is forbidden, except with the person's express consent "laissant une trace écrite" or in a few other cases (14). Such data needs INPDP authorisation, **except health data** (15). Health data falls under chapter V | Accommodation flags can reveal a disability, so they are treated as health data (MR-A1) |
| No conditioning | 17 | It is forbidden to make a service or advantage conditional on accepting processing for other purposes | Optional features need separate consents, and Kuizi must work without them, the AI tutor included (MR-C5, MR-T8) |
| Security and processors | 18–20, 23 | A list of security precautions (18, 19). Processors are chosen carefully and act only within the controller's instructions; both are civilly liable (20). Confidentiality continues after processing ends (23) | Vendor agreements (T236); staff confidentiality undertakings (MR-G5) |
| Nationality and residence | 22 | The natural person processing data, or the legal representative of a legal person, **and their agents** must be of **Tunisian nationality, resident in Tunisia, and have no criminal record**. "Ces conditions s'appliquent également au sous-traitant et à ses agents" | Raises questions for Kuizi's legal entity and for foreign processors and their staff (AWS, LLM providers). Open question Q8 |
| End of activity | 24 | The INPDP must be told 3 months before processing stops for good | Belongs in the business-continuity and exit plan |
| Consent | 27 | Consent must be "**exprès et écrit**". For a person without legal capacity, the general rules of law apply. "La personne concernée ou son tuteur peut, à tout moment, se rétracter" | The child as well as the tutor can withdraw (MR-C7, Q7). Whether electronic consent counts as written is Q5 |
| **Children** | **28** | "Le traitement des données à caractère personnel qui concerne un enfant ne peut s'effectuer qu'après l'obtention du consentement de son tuteur et de l'autorisation du juge de la famille." The judge may order processing without the tutor's consent when the child's best interest requires it, and may withdraw the authorisation at any time | **Applies to every pupil.** Kuizi cannot rely on parental consent alone (MR-C1, Q1–Q3) |
| Exceptions to consent | 29 | No consent is needed when processing is clearly in the person's interest and they cannot be reached, when consent would need disproportionate effort, or when a law or a contract to which the person is a party provides for the processing | Whether a contract signed by the parent sets article 28 aside is unclear (Q1); this draft assumes it does not |
| Purpose and advertising | 30 | Consent covers only the form and purpose it was given for. Advertising use needs "consentement exprès et particulier", and article 28 applies for a child | No advertising at all (MR-M1) |
| Information | 31 | The person must be told, by a means that leaves a written trace, about the data, the purposes, whether answering is compulsory, the recipients, the controller, their rights (access, withdrawal, objection), the retention period, the security measures and any country of transfer. Notice is given "**dans un délai d'un mois au moins avant la date fixée pour le traitement**" | Notice to parents (T207, NEW-3). The one-month notice period could delay every account activation (Q6) |
| Access | 32–41 | The person, their heirs **or their tutor** may consult, correct and erase data, and get a copy in clear language within one month (32, 38, 40). Requests for rectification can be made electronically (37). Disputes go to the INPDP | Parents have a legal right of access, which must be weighed against the child's privacy (Child Protection Code art. 6, MR-F2, Q17) |
| Objection | 42, 43 | Right to object for valid, legitimate and serious reasons, and to object to communication for advertising; an objection suspends processing at once (42). **When the person is a child, the family judge decides objection disputes** (43) | The objection flow goes in the parent dashboard (T097) |
| Collection | 44 | Data is collected from the person themselves. Collection from third parties needs consent, and article 28 applies for a child | Affects school roster imports (T093, MR-E2) |
| Destruction | 45 | Data is destroyed when its retention period ends or its purpose is achieved. **A bailiff's report is drawn up in the presence of an expert named by the INPDP**, at the controller's cost | How this applies to routine automated deletion is Q11 (T018, MR-R2) |
| Communication to third parties | 47, 48 | Communication needs express consent leaving a written trace; article 28 applies for a child. The INPDP can authorise it if the person refuses, in certain cases | Covers any sharing with schools that are not the controller, researchers or partners |
| Reuse for research | 49 | Further use for historical or scientific purposes needs consent and INPDP authorisation; article 28 applies for a child | Pedagogical experiments (T055) may count as research (Q14, MR-X2) |
| **Transfers abroad** | 50–52 | Forbidden if harmful to public security or Tunisia's vital interests (50). Only to countries with adequate protection (51). "**Dans tous les cas**", INPDP authorisation is required, with a decision within one month (52). "**Lorsque les données … concernent un enfant, la demande est présentée au juge de la famille**" (52) | Every flow out of Tunisia needs authorisation, and for pupils the request goes to the family judge (MR-R3, NEW-6, Q9) |
| Public bodies | 53, 54, 57 | Processing by public authorities and public establishments that is needed for their missions is exempt from articles 7, 8, 13, **27, 28**, 37, 44 and 49 (53, 54). Public bodies may not pass data to private persons without express consent; article 28 applies for a child (57) | A possible route through public schools or the Ministry, with Kuizi as their processor (Q2). Article 57 limits what a public school may hand to Kuizi |
| Health data | 62–65 | Health data may be processed with the consent of the person or their tutor (article 28 applies for a child), when the law provides for it, or for public health, care or research (62). It may be processed **only by doctors or by people bound to professional secrecy** (63). No longer than necessary (64). The INPDP may set measures and forbid publication (65) | Accommodation flags (MR-A1, MR-A2, Q10) |
| Video surveillance | 69–74 | Needs prior INPDP authorisation; allowed only in listed places | Kuizi never uses camera-based proctoring or webcam features (MR-D5) |
| INPDP powers | 76, 77, 81, 82 | Authorisations, complaints, inspections, withdrawal of authorisation, a ban on processing; appeals go to the Tunis Court of Appeal | |
| Penalties | 86–101 | 2 years in prison and a 10,000 TND fine for breaching article 28 paragraph 1, 14 paragraph 1 or 63 paragraph 1, and the same for article 27 paragraph 1, 31, 44 or 68 (87). 1 year and 5,000 TND for processing without a declaration or authorisation, **transferring abroad without INPDP authorisation**, or communicating data without consent (90). 3 months and 1,000 TND for breaching articles 12, 18, 19, 20 (paragraphs 1 and 2), 21, 37, 45, 64 or 74 (94). The legal or de facto manager of a legal person is personally liable (101) | The product owner, as manager, carries personal criminal exposure. This is why the article 28 and 52 questions come first |

### 2.2 What Law 2004-63 does not contain

These points come from reading the full text; counsel should confirm them.

- **No age of digital consent.** A child (under 18) never consents alone. The tutor consents, and the family judge authorises (art. 28).
- **No obligation to notify breaches.** Articles 18 and 19 cover security, but no article requires telling the INPDP or the people affected about a breach. T216 therefore needs counsel to define the notifications (Q12). Convention 108+ would add a duty to notify the authority, if Tunisia ratifies it and it enters into force (section 2.6).
- **No article on profiling or automated decisions.** The principles in articles 9 and 11 still apply. Section 3 brings in good practice (MR-P).
- **No general duty to carry out a DPIA.** Kuizi keeps T017 anyway, because the INPDP can impose measures (art. 15, 65, 76) and because good practice expects one.

### 2.3 Who consents: the tutor

Article 28 requires the consent of the child's **tuteur**. Under the Code of Personal Status, the father is the legal tutor of a minor child. A mother who has been given custody exercises the tutor's prerogatives for the child's **studies**, travel and financial accounts [Unconfirmed: Code of Personal Status art. 154 and 67]. Two consequences for design:

- The consent flow records who is consenting and in what capacity: father as legal tutor, mother with custody, or another appointed tutor (MR-C2).
- Separated parents, parents who disagree, and a parent who refuses while the other agrees all need a written rule from counsel (Q4). Disputes about objections go to the family judge (art. 43).

### 2.4 Child Protection Code (Law 95-92 of 9 November 1995, in force 11 January 1996)

All articles below are **[Confirmed]** in the annotated edition, which may predate later amendments (Q23).

| Article | What it says | What it means for Kuizi |
| --- | --- | --- |
| 3 | A child is anyone under 18 who has not reached majority under special laws | Every pupil is a child |
| 4 | The child's best interest is "une considération majeure" in every measure taken by courts, administrative authorities and public or private social-protection institutions. Account is taken of the child's needs, age, health and family setting | Kuizi is none of these bodies, but this standard guides counsel and the safeguarding policy [Good practice for Kuizi] |
| 6 | Every child has the right to respect for their private life, taking into account the rights and responsibilities of their parents | How much parents see in band B (MR-F2) |
| 7 | Parents have the primary responsibility for the child's education and schooling | Parents control band A (MR-F1) |
| 10 | The child may express opinions freely, and these are weighed according to age and maturity | Child assent in both bands (MR-C6) |
| 20 | Lists the difficult situations that threaten a child: (a) loss of parents; (b) neglect and vagrancy; (c) a notorious failure of education and protection; (d) habitual ill-treatment; (e) sexual exploitation; (f) exploitation in organised crime; (g) begging and economic exploitation; (h) parents unable to protect and educate the child | The categories of concern for the safeguarding policy (T222) |
| 28–30 | A *délégué à la protection de l'enfance* in each governorate, who intervenes when a child's health or integrity is threatened | The safeguarding escalation route (MR-G1) |
| 31 | "**Toute personne, y compris celle qui est tenue au secret professionnel**" must report situations (d) and (e) to the délégué. Anyone **may** report the other situations. Reporting every article 20 situation is **mandatory for people whose role is to protect and assist children**: educators, doctors, social workers | Kuizi staff and its safeguarding lead fall at least under the first paragraph. Whether they are "chargées de la protection" is Q16 |
| 32 | Every adult must help a child who comes to them to inform the délégué or report a threat | Applies when a pupil asks Kuizi for help (MR-G2) |
| 33, 34 | No one may be prosecuted for a report made in good faith. The reporter's identity may not be disclosed without their consent | Safeguarding records and confidentiality (MR-G4) |
| 40, 42 | From 13, the child reads and signs agreements and must be told they can refuse the proposed measure | Supports the threshold between bands A and B (section 1) |

**Helplines** [Unconfirmed; T222 confirms them before anything goes into product copy]:

- **1809**: the free line of the Ministry of Family. It offers listening and psychological support and receives reports, which it passes to the délégués.
- **192**: a second reporting line. Sources disagree on whether it runs only during office hours or around the clock.
- Emergency numbers: police 197, SAMU 190, civil protection 198.

### 2.5 School context

- **School structure** [Unconfirmed: Law 2002-80 of 23 July 2002, *loi d'orientation*]. Basic education lasts 9 years (6 primary and 3 preparatory) and is compulsory from 6 to 16. 6e ends primary school and leads to the entrance exam for the *collèges pilotes*. 9e ends basic education and leads to the entrance exam for the *lycées pilotes*.
- **Public schools are public bodies.** That brings in articles 53–57 of Law 2004-63 (section 2.1). The Ministry of Education and its Centre national des technologies en éducation (CNTE) already run official platforms: pupil enrolment, "L'école de la Tunisie du futur" (2024), "Vie scolaire" (2026) and a free tutoring platform (edusoutien.education.tn, March 2026) [Unconfirmed: press]. A partnership with the Ministry is both a legal route (Q2) and a competitive question for the product owner.
- **The INPDP expects pupils' data to stay in Tunisia.** In 2021 the INPDP publicly objected to the Ministry using Google Forms for a pupil survey. It called the use of foreign platforms a clear breach of the 2004 law and cited a 5 November 2020 circular requiring e-services of administrative bodies to be hosted in Tunisia [Unconfirmed: press; the circular's number and scope are Q9]. Kuizi should expect close scrutiny of foreign hosting for pupils' data.
- **Use in schools.** No rule on private ed-tech in schools was found. Whether the Ministry must authorise Kuizi before it is used in public schools is Q15 (NEW-10).

### 2.6 International commitments

| Instrument | Tunisia's status | Consequence |
| --- | --- | --- |
| Council of Europe Convention 108 and Additional Protocol (ETS 181) | **Party since 1 November 2017** (the 51st party); Parliament approved accession in May 2017 [Confirmed: Council of Europe] | Binding treaty principles: data quality, special categories such as health only with appropriate safeguards, rights of the data subject, and transborder flows only to adequate countries (Protocol art. 2). Approved treaties rank above ordinary law [Unconfirmed: constitutional article] |
| Convention 108+ (amending Protocol CETS 223) | **Signed in May 2019** [Unconfirmed: press]. Ratification not confirmed (Q22). The Protocol is **not yet in force**: 34 of the 38 required ratifications as of June 2026 [Council of Europe T-PD reports] | Good practice now, and binding once ratified and in force: notify the authority of breaches, assess impact before processing, a right not to be subject to purely automated decisions, and particular attention to children [article numbers to confirm] |
| UN Convention on the Rights of the Child | Ratified by Law 91-92 of 29 November 1991 [Confirmed: cited in the Child Protection Code edition] | General Comment No. 25 (2021) on the digital environment calls for no commercial profiling or targeting of children, privacy by design and safety by design, and respect for evolving capacities [Good practice; paragraph numbers to confirm] |

### 2.7 Reform in progress

A new draft organic law on personal data (132 articles) was filed by members of parliament in July–August 2025. In February 2026 it was being studied in committee [Unconfirmed: press]. It would create a new authority, require DPOs in public bodies, change the transfer rules, and add a few articles on AI. No source shows it has been adopted, and its rules for children are unknown. **Kuizi must comply with Law 2004-63 now**, while keeping consent and age rules configurable so a new law can be absorbed (Q21).

## 3. Good-practice references (design rules, not obligations in Tunisia)

### 3.1 UK Age Appropriate Design Code (ICO, 2020)

Kuizi adopts the 15 standards as design rules. Its age ranges include 10–12 ("transition years") and 13–15 ("early teens"), which match bands A and B.

| # | Standard | Kuizi rule |
| --- | --- | --- |
| 1 | Best interests of the child | Child Protection Code art. 4 standard used in every DPIA decision (T017) |
| 2 | Data protection impact assessment | T017 covers both bands (section 5.2) |
| 3 | Age-appropriate application | Bands A and B (section 1, MR-C9) |
| 4 | Transparency | Child-friendly notices for each band in French and Arabic (NEW-3, section 7) |
| 5 | Detrimental use of data | No engagement profiling and no inference of health or emotions (MR-P2, MR-D8) |
| 6 | Policies and community standards | Tutor rules and safeguarding are enforced, not only published (MR-T4, MR-G) |
| 7 | Default settings | Everything optional is off by default (MR-C5, MR-S, MR-N) |
| 8 | Data minimisation | MR-I3, MR-D1 to MR-D9 |
| 9 | Data sharing | No sharing beyond processors and the school (MR-E1, MR-R4) |
| 10 | Geolocation | Never collected (MR-D5) |
| 11 | Parental controls | The child is told when controls are on (MR-F3) |
| 12 | Profiling | Learning only; never for significant decisions (MR-P1) |
| 13 | Nudge techniques | No streak pressure, guilt copy or "one more" loops (MR-S5, MR-S9) |
| 14 | Connected toys and devices | Not applicable; home-screen widgets show no personal data on the lock screen (MR-N8) |
| 15 | Online tools | Rights exercised in the app, with export and deletion (MR-F4) |

### 3.2 GDPR article 8 and the EU AI Act

- **GDPR art. 8** [Good practice]. A child can consent alone to an online service from 16; Member States may lower this to 13. Below that age, the holder of parental responsibility consents, and the controller must make "reasonable efforts" to verify this, taking available technology into account. Related provisions:
  - recitals 38 and 58 (children need specific protection and clear language);
  - art. 12(1) (information addressed to a child in plain language);
  - art. 17(1)(f) (erasure of data collected from a child);
  - art. 22 and recital 71 (decisions based solely on automated processing "should not concern a child");
  - art. 25 (data protection by design and by default) and art. 35 (impact assessment).
- **France** sets 15 and requires the joint consent of the minor and the parent below that age [Unconfirmed: Loi Informatique et Libertés, art. 45]. This is a useful comparison because Tunisian practice often follows French models.
- **EU AI Act (Regulation 2024/1689)** [Good practice]. It does not apply in Tunisia, but:
  - Annex III point 3 classes AI in education as **high-risk** when it evaluates learning outcomes (including to steer learning), assesses the appropriate level of education, or detects prohibited behaviour during tests. Kuizi's knowledge tracing and any cheating detection fall into these descriptions.
  - Art. 5(1)(b) forbids exploiting vulnerabilities due to age.
  - Art. 50(1) requires telling people that they are interacting with an AI system.

### 3.3 COPPA (United States, children under 13)

COPPA is 15 U.S.C. 6501–6506 and 16 CFR Part 312 [Good practice; Kuizi is not a US service].

- **Verifiable parental consent** (§312.5): methods "reasonably calculated" to make sure the person consenting is the parent. Examples include a signed form, a payment transaction, a call or video call with trained staff, or a check of a government ID followed by deletion.
- The **2025 amendments** (published 22 April 2025, in force 23 June 2025, compliance by 22 April 2026):
  - a separate consent for disclosure to third parties, including for targeted advertising;
  - a written data-retention policy, published in the privacy notice;
  - a written information-security programme;
  - new consent methods: knowledge-based questions, ID with face match, and text messages in some cases;
  - proposed rules for ed-tech and schools were dropped.
- §312.7: a child's participation may not depend on giving more data than is reasonably necessary (compare art. 17 of Law 2004-63).
- **School authorisation**: FTC guidance (not the Rule) lets a school consent in the parent's place for use limited to the school's educational purposes, with no commercial use. This is a useful model for the school channel (MR-C3).

### 3.4 UNICEF Guidance on AI and children, version 3.0 (December 2025)

Its 10 requirements, and the Kuizi rules that answer them [Good practice]:

1. Regulation, oversight and compliance: T017 and the counsel opinion (NEW-1).
2. Safety for children: MR-T, MR-G.
3. Data and privacy: MR-D, MR-R.
4. Non-discrimination and fairness: MR-P6.
5. Transparency, explainability and accountability: MR-P4, MR-T4.
6. Responsible practice that respects children's rights: MR-T6 (vendor terms).
7. Best interests, development and well-being: MR-N6, MR-S9.
8. Inclusion: MR-A, and accessibility in E14.
9. Preparing children for AI: the tutor explains what AI is (MR-T4).
10. An enabling environment: research with children (MR-X).

The new section on AI companions supports MR-T4: no companion persona.

### 3.5 Store and vendor rules [Contract]

| Source | Rule | Kuizi impact |
| --- | --- | --- |
| Apple guideline 1.3 (Kids Category) | No links out of the app, purchase opportunities or other distractions except behind a parental gate. No personal data sent to third parties; no third-party analytics or advertising, with narrow exceptions | Whether to list in the Kids Category is decided in T169. Its age ranges (5 and under, 6–8, 9–11 [Unconfirmed]) cover only Kuizi's 11-year-olds |
| Apple 5.1.4 (Kids) | Apps intended mainly for kids should not include third-party analytics or advertising. Birth date and parental contact may be collected only to comply with children's privacy laws | MR-D5, MR-M1 |
| Apple 5.1.2(i) | Clear disclosure, and explicit permission, before personal data is shared with third parties, "including with third-party AI" | The AI tutor consent (MR-C5) |
| Apple 4.8 | Apps that offer a third-party login must also offer an equivalent privacy-preserving login | Applies to parent sign-in if Google is offered to parents (MR-I2) |
| Apple 5.1.1(v) | Account deletion must be available in the app | T167 |
| Google Play Families policy | For children and users of unknown age: no transmission of the advertising ID or other device identifiers, no location for child-only apps, only approved ads SDKs (Kuizi uses none), and no authentication service whose terms bar use by children | Google Sign-In for pupils is a risk (MR-I2). Data safety and target-audience declarations go in T169 |
| OpenAI under-18 API guidance | Do not process personal data of children under 13 without first using zero data retention. Use age-appropriate content filters, monitoring with escalation for high-risk interactions, age assurance where appropriate, and disclosures to minors. OpenAI may audit | MR-T6. Band A sends no pupil text at all (MR-T1) |
| Anthropic guidelines for organisations serving minors | Age verification, content moderation, monitoring and reporting, educational resources, Anthropic's child-safety system prompt, compliance with child-privacy laws and a **public statement of that compliance**, and disclosure that the user is talking to an AI | MR-T4, MR-T6, T236 |

## 4. Product rules by age band

Each rule has an ID (`MR-…`) that tickets cite. "Both" means bands A and B. The Source column gives the reason for the rule. **Defaults** marked *(proposal)* are values for the product owner to decide; no law sets them.

### 4.1 Consent, verification and the child's assent

| ID | Band A (11–12) | Band B (13–15) | Source |
| --- | --- | --- | --- |
| MR-C1 | A pupil account shows no learning content and sends no learning events until two things are recorded: (a) a verified consent from the tutor, and (b) the article 28 condition counsel chooses (the family judge's authorisation, or the public-school route). Both bands | | 2004-63 art. 27, 28, 87; Q1–Q3 |
| MR-C2 | The consenting person declares their capacity (father as legal tutor, mother with custody, other appointed tutor), and the record keeps it. Rules for separated or disagreeing parents follow counsel's answer. Both bands | | Code of Personal Status [Unconfirmed]; Q4 |
| MR-C3 | **School channel**: the school confirms the parent–pupil link from its own records. **Direct (B2C) channel**: a one-time code sent to the parent's Tunisian mobile, a declaration of capacity, and a confirmation message 24 hours later with a one-tap "this was not me" link that cancels. **At launch, band A joins only through the school channel**, until counsel approves a stronger direct method | School channel and direct channel as described, both open | COPPA §312.5 and GDPR art. 8(2) [Good practice]; Q24 |
| MR-C4 | No copies of the national ID card (CIN), birth certificates or tutorship documents. If counsel or the judge needs proof of tutorship, the school or the court holds it, not Kuizi. Both bands | | 2004-63 art. 11; Q4 |
| MR-C5 | Separate consents, each one refusable without losing the core service: (1) core adaptive learning; (2) accommodation data; (3) the AI tutor (LLM processing and transfer abroad); (4) notifications on the child's own device; (5) research and experiments. Advertising and marketing to the child are not offered at all | The same five, plus (6) class leaderboards and class duels | 2004-63 art. 17, 30, 49, 52; Apple 5.1.2(i) |
| MR-C6 | Child assent: an explanation in pictograms with audio, in French and Arabic, then "J'ai compris". The child can answer "pas maintenant", and the account then waits | The pupil's own agreement is recorded next to the parent's consent, and a refusal by the pupil is respected (counsel to confirm its legal effect) | Child Protection Code art. 10, 40, 42; Q7 |
| MR-C7 | The tutor **or the pupil** can withdraw any consent at any time. Processing stops within 1 minute (T013), and the other party is told. Disputes go to the family judge. Both bands | | 2004-63 art. 27 para. 2, 43 |
| MR-C8 | The parent gets the article 31 information in writing, by a means that leaves a written trace, before activation. When it must arrive follows counsel's answer on the one-month rule. Both bands | | 2004-63 art. 31; Q6 |
| MR-C9 | Moving to band B: on the first day of the month after the 13th birthday, the account moves to band B. The new band B features stay off until both the pupil and the parent switch them on, and both are told | (Pupils aged 16 or more in these grades keep band B rules) | Section 1; Q18 |

### 4.2 Accounts and identity data

| ID | Band A | Band B | Source |
| --- | --- | --- | --- |
| MR-I1 | Pupil accounts are created by a parent or a school, never by the pupil alone (self-registration stays off). Both bands | | 2004-63 art. 28 |
| MR-I2 | No social sign-in (Google, Apple) for pupils. School-managed education accounts only if counsel accepts them (T094) | School SSO allowed where the school manages pupil accounts | Google Play Families (authentication services whose terms bar children); Google account minimum age [Unconfirmed] |
| MR-I3 | Data about the pupil is limited to: first name or a chosen nickname, school and class (if any), grade (6e–9e), **birth month and year** (to derive the band only; encrypted; never in events), language and comfort settings. Kuizi does not collect a pupil's email, phone number, photo, address, CIN, gender or nationality. Both bands | | 2004-63 art. 11; AADC 8 |
| MR-I4 | Usernames are generated and contain no real name. Other pupils only ever see a generated nickname. No free-text display names and no photo avatars: preset avatars only. Both bands | | AADC 7, 8; NEW-8 |
| MR-I5 | Access tokens carry a coarse `age_band` claim (A or B) so services can enforce these rules. Never the birth date. Both bands | | `docs/dev/identity.md` (lightweight tokens) |
| MR-I6 | A child-friendly sign-in method (for example a class card with a QR code at school, and a parent-managed password at home) **after a security review in T215**. The 12-character password rule is not weakened without the threat model | Current password policy | Security; product owner decision |

### 4.3 AI tutor

| ID | Band A | Band B | Source |
| --- | --- | --- | --- |
| MR-T1 | **No open chat.** The tutor helps only through suggested requests ("Je ne comprends pas la question", "Un indice", "Un exemple semblable"), the hint ladder and the maths keypad. There is no free-text box, and the pupil's text never reaches an LLM | Free text only inside an exercise ("pose une question sur cet exercice"), at most 300 characters *(proposal)*, with a visible reminder not to share personal information. No image upload. Off-topic requests are declined politely | AADC 5, 12; OpenAI zero-data-retention rule for under-13s; UNICEF requirements 2 and 3 |
| MR-T2 | — | A filter removes names, phone numbers, emails, addresses and CIN-like numbers before text reaches the LLM and before it is stored (NEW-5) | 2004-63 art. 11, 52 |
| MR-T3 | Only IDs of the requests and hints are stored, never text | Conversation text kept **30 days** *(proposal)* for continuity and safety review, then deleted. Never used to train any model. Not shown to teachers or parents, except in a safeguarding escalation (T222) | 2004-63 art. 11, 45; Child Protection Code art. 6 |
| MR-T4 | The tutor always says it is an AI. It has no human persona, does not claim feelings and offers no companionship. It never asks for personal information, never encourages secrecy, never suggests contacting or meeting anyone, and steers personal topics back to the lesson (pointing to help when needed, MR-G2). Both bands | | Anthropic and OpenAI minors guidance [Contract]; EU AI Act art. 50; UNICEF (AI companions) |
| MR-T5 | Hints, not answers (T070). Reading level fits the grade. The judge also checks that content suits the age. Both bands | | AADC 3 |
| MR-T6 | Only LLM providers with a signed DPA, zero data retention, no training on Kuizi data, the minors-use terms met (age assurance, moderation, monitoring, child-safety prompt, public compliance statement) and an authorised transfer. Requests carry no pupil ID, tenant ID or name. If an LLM is used for band A at all (for example to word a hint from a template), a model hosted by Kuizi or in Tunisia is preferred | Same rules for the provider | 2004-63 art. 20, 22, 52; vendor terms; Q8, Q9 |
| MR-T7 | Dictation is recognised **on the device only**, so no audio leaves it | A server fallback only with the AI tutor consent. Audio is never stored (existing rule) | Accessibility requirement FR-A8, section 3 of that document |
| MR-T8 | Kuizi works fully without the AI tutor, through the authored hint ladder, for families that refuse that consent. Both bands | | 2004-63 art. 17 |
| MR-T9 | Time with the tutor counts towards the screen-time limit (MR-N6). Both bands | | AADC 13 |

### 4.4 Telemetry and data minimisation

| ID | Band A | Band B | Source |
| --- | --- | --- | --- |
| MR-D1 | Only events the learning service needs. Allowed in both bands: `item.presented`, `item.answered`, `hint.requested`, `hint.shown`, `session.start`, `session.end`, `focus.*`, `tts.played` | | 2004-63 art. 10, 11 |
| MR-D2 | `item.interaction` (hover, focus, typing bursts) and `item.hesitation` are **not sent**. Widget values that form part of the answer stay in `item.answered` | Sent only if the T047 gate shows they improve predictions for this age group. Otherwise their collection stops, rather than the data simply going unused. At most 3 months raw *(proposal)* | AADC 8; ML review conditions |
| MR-D3 | `response.expression` accepts only maths keypad input (digits, operators, allowed variables, units), and ingestion rejects anything else. Both bands | | 2004-63 art. 11 (no personal data in free text) |
| MR-D4 | `notification.*` events are kept to prove that protected windows were respected (T161), never to build individual send-time models (MR-N5). Both bands | | AADC 12 |
| MR-D5 | No third-party analytics or advertising SDKs, advertising IDs, device fingerprints, location, contacts, camera or video. The microphone is used only for on-device dictation. Both bands | | Apple 1.3, 5.1.4; Play Families; 2004-63 art. 69 |
| MR-D6 | Product analytics: aggregate counts only, with no individual journeys | Aggregated, with at least 10 pupils in any reported group *(proposal)* | AADC 8 |
| MR-D7 | Ingestion enforces the band rules on the server, using the `age_band` claim. Events not allowed for the band are dropped and counted. Both bands | | NEW-7 |
| MR-D8 | Kuizi **never infers** disability, health, emotions or family situation from telemetry, whether from hesitation, timing or any other signal. Both bands | | 2004-63 art. 14 ("indirectly"); AADC 5 |
| MR-D9 | Raw learning telemetry kept **12 months** *(proposal, instead of 24)*, then aggregated or deleted. Fine-grained events at most 3 months. Everything is erased when the account is deleted. Both bands | | 2004-63 art. 11, 45; Q20 |

### 4.5 Profiling and automated decisions

| ID | Band A | Band B | Source |
| --- | --- | --- | --- |
| MR-P1 | Knowledge tracing and routing are used only to choose the pupil's exercises, hints and reviews. Their results are **never** used for orientation, admission to collèges or lycées pilotes, grades, discipline or class placement, and school contracts forbid such use. Both bands | | GDPR art. 22 and recital 71, EU AI Act Annex III(3), Convention 108+, AADC 12 [Good practice] |
| MR-P2 | No engagement profiling: no churn prediction, no individual send-time optimisation, no engagement A/B tests | Experiments only in aggregate and with DPO approval for each one; no churn model | AADC 5, 12, 13 |
| MR-P3 | Mastery is shown as states (shapes and words), never as percentages or probabilities of failure. No predicted exam score | An optional "exam readiness" estimate with an uncertainty band, shown only to the pupil and parent, off by default, never to teachers as a ranking | AADC 5; T187 |
| MR-P4 | The pupil can see, in simple words, why an exercise was proposed. The parent can ask a person (a teacher or Kuizi support) to review or reset the mastery estimate. "Recommencer ce chapitre" resets it. Both bands | | UNICEF requirement 5; GDPR art. 22(3) [Good practice] |
| MR-P5 | No automated flag accusing an individual pupil of cheating, collusion or disengagement. Integrity signals are aggregated per test or item. Any concern about one pupil needs human review, is explained to the pupil and parent, can be contested, and never triggers an automatic sanction. Both bands | | EU AI Act Annex III(3)(d) [Good practice] |
| MR-P6 | Fairness is checked by band and grade, language, school type and accommodation (T047). No gender or region features without a lawful source. Both bands | | Existing open question in `product-owner-decisions.md` |

### 4.6 Gamification, leaderboards, duels and social features

| ID | Band A | Band B | Source |
| --- | --- | --- | --- |
| MR-S1 | No public leaderboards, no names in any ranking seen outside the class, and no school or national leaderboards. Both bands | | AADC 7; Child Protection Code art. 6 |
| MR-S2 | No individual leaderboards. Shared class goals instead ("notre classe a révisé 200 notions"), and personal progress against the pupil's own past | Class leaderboard, **off by default** (pupil and parent switch it on), under generated nicknames, ranked by mastery gain, showing the top 10 and the pupil's own position *(proposal)* | AADC 5, 7 |
| MR-S3 | No duels against other pupils, except **teacher-run class battles** in the classroom (the whole class, nicknames, no chat, no spectators from outside). Practice against a bot or one's own past attempts is allowed | Duels **only with classmates** (same school and class), or with a friend added by a code exchanged in person, if the parent setting allows it. No open matchmaking across schools or Tunisia, no spectators beyond teacher-run battles, no text or voice chat. A few positive preset reactions; block and report available | AADC 6, 7; T215 threat model |
| MR-S4 | No pupil-to-pupil messages, comments, forums, public profiles, followers, visible friend lists, user-generated content or public sharing of pupils' work. Both bands | | AADC 6, 7, 9 |
| MR-S5 | No daily streaks: weekly goals that never reset punitively | Optional streaks with automatic freezes. No loss-framed copy, and no notifications about streaks | AADC 13; FR-N6 |
| MR-S6 | Certificates and badges are private by default and shared only by the parent | Shared by the pupil if the parent allows it | AADC 7, 9 |
| MR-S7 | The public verification page shows only the first name and initial and the achievement: no school, no photo. The link expires after 90 days *(proposal)*. Both bands | | 2004-63 art. 47 |
| MR-S8 | Rewards cannot be bought. No loot boxes, random rewards or purchasable virtual currency. Both bands | | AADC 13 |
| MR-S9 | No nudges to keep playing: no autoplay or "encore un", no countdowns outside exam practice, no guilt copy. Both bands | | AADC 13; FR-N6 |

### 4.7 Notifications and screen time

| ID | Band A | Band B | Source |
| --- | --- | --- | --- |
| MR-N1 | By default, no push, SMS or email to the child. Reminders and account or security messages go to the parent. The parent may allow in-app reminders on the child's device, at most 1 a day | Push to the pupil's device only if the pupil and parent switch it on. Default budget of **1 useful message a day**, adjustable up to 3 *(proposal; FR-N4 says 2 and T157 up to 5)* | AADC 7, 13 |
| MR-N2 | Quiet hours of **20:00–08:00** *(proposal)*. The parent can make them stricter, not looser | Quiet hours of **21:00–07:30** on school nights *(proposal; FR-N3 says 22:00–07:00)* | AADC 13 |
| MR-N3 | Never during class hours (T153). Both bands | | FR-N3 |
| MR-N4 | No re-engagement, lifecycle or marketing messages to pupils. Lifecycle messages go to parents only, with their consent. Both bands | | 2004-63 art. 30 |
| MR-N5 | No individual send-time model (T154). Fixed windows, chosen within the allowed hours by the parent (band A) or by the pupil within the parent's limits (band B) | | AADC 12 |
| MR-N6 | The parent sets a daily limit (suggested **45 minutes** on school days *(proposal)*). Break prompt every 20 minutes. Calm summary at the end of a session. "Time to rest" at a bedtime the parent sets. The limit never cuts off an exam-practice paper without saving it | Suggested limit of **60 minutes** *(proposal)*; break prompt every 25 minutes | AADC 13; UNICEF requirement 7 |
| MR-N7 | Focus sessions of 15 or 25 minutes (45 is hidden) | 15, 25 or 45 minutes | FR-F1 |
| MR-N8 | Lock screens and home-screen widgets show no scores, names or duel status by default. Both bands | | AADC 14 |

### 4.8 Teachers and schools

| ID | Band A | Band B | Source |
| --- | --- | --- | --- |
| MR-E1 | The roles in each school contract follow counsel's answer. Either the school is the controller and Kuizi its processor (a processor is not a third party, art. 6; art. 20; for public schools art. 53–57), or Kuizi is the controller with the parents' consent. Both bands | | Q2, Q3 |
| MR-E2 | No import of pupils' personal data from a school (CSV, T093) unless counsel confirms the route: Kuizi as processor and the school with its own lawful basis, or parental consent first. By default the school hands out class join codes, and parents enrol and consent. Both bands | | 2004-63 art. 44, 47, 57, 28 |
| MR-E3 | For their own classes, teachers see mastery by concept, assignment completion and results, accommodations that have been shared (MR-A3) and aggregated class analytics. They do not see raw telemetry, timestamps of home activity, tutor text, notification data or other classes. Live "struggling now" feeds work only during a class session the teacher runs. Both bands | | AADC 8; 2004-63 art. 11 |
| MR-E4 | Learning alerts (mastery dropping on an assigned chapter) are allowed. No disengagement alerts based on home use | Disengagement alerts weekly at most, and only about assigned work | AADC 5 |
| MR-E5 | Teacher private notes contain no health, discipline, family or behaviour judgements. The parent can see them on request, and they are deleted at the end of the school year. Both bands | | 2004-63 art. 32, 14 |
| MR-E6 | Announcements are one-way (T227). No private messages between teachers and pupils. Both bands | | T227 AC2 |
| MR-E7 | Every time a teacher opens a pupil's profile, it is audited (T022, T226). Both bands | | 2004-63 art. 19 |
| MR-E8 | No use in public schools until the Ministry question is answered (NEW-10). Both bands | | Q15 |

### 4.9 Parents and transparency to the child

| ID | Band A | Band B | Source |
| --- | --- | --- | --- |
| MR-F1 | The parent dashboard is the control centre: consents, settings, notifications, time limits, accommodations and sharing, plus the weekly summary (T075) | The parent sees a progress summary, time used and the consents | Child Protection Code art. 7 |
| MR-F2 | — | By default the parent does not see tutor text or the item-by-item log. The legal access right (art. 32) is handled through a formal request, following counsel's answer | Child Protection Code art. 6; 2004-63 art. 32; Q17 |
| MR-F3 | The pupil always sees what parents and teachers can see ("Ce que voient tes parents"), and an indicator shows when parental controls are on. Both bands | | AADC 11 |
| MR-F4 | The parent can export (a copy within one month) and delete the child's data in the app (T018, T167). Both bands | | 2004-63 art. 32, 38, 40 |

### 4.10 Accommodations

| ID | Band A | Band B | Source |
| --- | --- | --- | --- |
| MR-A1 | Treated as **health data**. Needs the tutor's consent plus the article 28 condition, kept apart from the core consent, and revocable (T151). Both bands | | 2004-63 art. 14, 62, 28 |
| MR-A2 | Only people bound by professional secrecy (staff confidentiality undertakings) may process accommodation data, pending counsel's answer on whether article 63 applies to flags such as "extra time". Both bands | | 2004-63 art. 63; Q10 |
| MR-A3 | The parent manages the flags and decides what teachers see, after asking the child | The pupil chooses which flags teachers see, within the parent's consent; the parent sees what is shared | Child Protection Code art. 7, 10; open decision "Who sees a minor's accommodations" |
| MR-A4 | Comfort presets are named by what they do ("lecture facilitée", "moins de distractions"), not by a diagnosis ("dyslexie", "TDAH"). Kuizi stores the settings, not a diagnosis label, and never asks a diagnosis question. Both bands | | 2004-63 art. 11, 14 |
| MR-A5 | The existing rules stay: no medical documents; the school attests the time multiplier; accommodations never appear in leaderboards, exports or LLM prompts. Both bands | | Accessibility requirements, section 3 |

### 4.11 Advertising, payments and marketing

| ID | Band A | Band B | Source |
| --- | --- | --- | --- |
| MR-M1 | No advertising of any kind in the pupil experience: no ads SDKs, no behavioural or contextual ads, no sponsored content. Data is never sold or rented. Both bands | | 2004-63 art. 30, 42; Apple 1.3, 5.1.4; Play Families |
| MR-M2 | No marketing to pupils and no referral rewards for pupils. Marketing addresses parents and schools. No real children in store screenshots or campaigns without the tutor's consent and whatever counsel requires for images of children. Both bands | | Q19 |
| MR-M3 | Purchases are made only by parents, through the parent account or behind a parental gate. No purchase prompts to pupils. The free plan is never used to pressure children ("tes amis ont Premium"). Both bands | | Apple 1.3; AADC 13 |
| MR-M4 | Claims made to parents and schools are backed by evidence (T199). Both bands | | Consumer protection |

### 4.12 Safeguarding

| ID | Band A | Band B | Source |
| --- | --- | --- | --- |
| MR-G1 | A named human safeguarding lead and a protocol (T222) built around Child Protection Code art. 31: reports to the délégué à la protection de l'enfance of the governorate; helplines and emergency numbers confirmed (section 2.4). Both bands | | Child Protection Code art. 28–34 |
| MR-G2 | A **"J'ai besoin d'aide"** button on every pupil screen. It shows the helplines and "parle à un adulte de confiance", with an optional request that a school adult contact the pupil (routed to the safeguarding lead, then the school contact). No text is stored for band A (NEW-9) | Same button | Child Protection Code art. 32 |
| MR-G3 | — | A safety classifier on every free-text message (T223). The safeguarding lead reviews high-severity flags within 15 minutes. **Never an automatic message to a parent when the concern may involve the family** | Child Protection Code art. 4, 31, 34 |
| MR-G4 | Safeguarding records are stored separately, with access limited to the safeguarding lead, and kept as long as counsel decides. The reporter's identity is protected. Both bands | | Child Protection Code art. 34; Q20 |
| MR-G5 | Everyone with access to pupils' data or the safeguarding queue signs a confidentiality undertaking, passes the vetting counsel requires (criminal-record check) and completes safeguarding training (NEW-12). Both bands | | 2004-63 art. 22, 23; T222 AC3; Q8 |
| MR-G6 | The threat model (T215) covers grooming, impersonation of a parent or teacher, bullying through duels and nicknames, sextortion and bypassing parent verification. Both bands | | AADC 6 |

### 4.13 Retention, erasure, transfers and vendors

| ID | Rule (both bands) | Source |
| --- | --- | --- |
| MR-R1 | A retention schedule for each data class, approved by the DPO. Proposals: the learning record lives while the account is active, and the account is **deleted (not pseudonymised)** after 12 months of inactivity, with a warning to the parent first. Tutor text 30 days. Raw telemetry 12 months; fine-grained events 3 months. Consent and safeguarding records as counsel decides | 2004-63 art. 11, 45, 64; Q20 |
| MR-R2 | The erasure pipeline produces an auditable deletion report for each batch, so that whatever article 45 requires (a bailiff's report with an INPDP expert) can be met | 2004-63 art. 45, 94; Q11 |
| MR-R3 | Every flow of pupils' data out of Tunisia (cloud hosting, LLM APIs, the warehouse, monitoring, crash reports, email and SMS providers) needs INPDP authorisation, with the request going to the family judge because the data belongs to children. **Until a flow is authorised, pupils' personal data stays in Tunisia.** Local-first development with synthetic data is unaffected | 2004-63 art. 50–52, 90; NEW-6; Q9 |
| MR-R4 | Processors are bound by contract (art. 20) and checked against article 22 as counsel interprets it. A public list of sub-processors is kept (T236) | 2004-63 art. 20, 22; Q8 |
| MR-R5 | No real children's data in development, tests or preview environments (existing ground rule, T219) | ADR 0005, ADR 0006 |

### 4.14 Research, testing and pilots

| ID | Rule (both bands) | Source |
| --- | --- | --- |
| MR-X1 | Usability tests, co-design rounds and pilots with children follow a written protocol (NEW-11): the tutor's consent plus the article 28 condition, the child's assent, a facilitator trained in safeguarding, two adults present, no video of faces unless separately agreed, recordings deleted after analysis, and synthetic accounts | 2004-63 art. 28, 66–68; Child Protection Code art. 10 |
| MR-X2 | Pedagogical experiments (T055): DPO approval for each experiment and parents informed. Reuse for research needs consent and INPDP authorisation (art. 49), depending on counsel's answer. No experiment ever withholds accessibility features | 2004-63 art. 49; Q14 |

## 5. What must change in the plan

The backlog and Jira belong to the main session; this section only proposes changes. New tickets are numbered NEW-1 to NEW-12 here; the main session gives them their T-numbers.

### 5.1 Order of work

1. **NEW-1** (counsel's opinion) comes first and blocks the "done" state of T013, T017, T093 and T236. T013 can still be built on synthetic data in Sprint 3, as long as the article 28 condition is configurable.
2. **T017** should depend on NEW-1 rather than on T013: the impact assessment should shape the consent design, not follow it. Proposal: NEW-1 → T017 (first draft) → T013 → T017 (signed).
3. **NEW-2** (age bands) and **NEW-7** (telemetry policy) come before T024 and T025 are closed, so that band rules are enforced from the first event.
4. **NEW-6** (data-residency ADR) comes before T240 (cloud move, Sprint 11), T059 sends real traffic, and T236 is signed.
5. **NEW-10**, **NEW-11** and **NEW-12** come before any work with real children: usability rounds (T183, T150) and the pilot (T108).

### 5.2 Existing tickets to change

**E02 Identity, security and compliance**

| Ticket | Jira | Sprint | Change | Rules |
| --- | --- | --- | --- | --- |
| T012 | KK-32 | S2 | In review: do not reopen; follow-ups go to NEW-2. The role table and documentation (`docs/dev/identity.md`) change: `student` becomes "pupil, 11–15; every account belongs to a minor". Google sign-in stays off for pupils. A child-friendly sign-in for band A is decided in T215 | MR-I1, I2, I5, I6 |
| T013 | KK-33 | S3 | **Rewrite.** Title: "As a parent or legal tutor, I give verifiable consent before my child (11–15) can use Kuizi". New acceptance criteria: (1) no pupil account reaches learning content or sends learning events until a verified tutor consent **and** the article 28 condition chosen in NEW-1 are recorded (automated test); (2) the consent record holds the policy version, time, declared capacity, verification method, each separate consent and the pupil's assent; the IP address is kept only if counsel needs it as proof; (3) the tutor or the pupil can withdraw any consent, which stops the affected processing within 1 minute and informs the other party. Blocked by NEW-1 before it can close. Suggest 5 → 8 points, or move the assent screens to NEW-3 | MR-C1–C9 |
| T017 | KK-37 | S4 | The scope becomes a service used only by children. The impact assessment covers article 28, articles 52 and 22, the article 31 timing, article 45, article 63, profiling of children, band B free text and every MR-* rule. Add an acceptance criterion: "Every MR-* rule is mapped to the risk it reduces; every remaining high risk has a ticket." Depends on NEW-1 (section 5.1) | All |
| T018 | KK-38 | S6 | Pupil accounts inactive for 12 months are **deleted** after a warning to the parent; they are not pseudonymised (this replaces the current criterion). Retention follows the DPO's schedule. Each deletion batch produces a report (article 45). A deletion request from a pupil is honoured and the parent is told | MR-R1, R2, C7 |
| T015 | KK-35 | S10 | Field-level encryption also covers the birth month and year, the declared capacity and the parent's contact details | MR-I3 |
| T022 | KK-42 | S10 | The audit log also covers consent, assent, withdrawal and the article 28 status, staff access to pupil accounts, and access to safeguarding records | MR-C7, G4 |
| T215 | KK-235 | S3 | The threat model adds child-specific threats (MR-G6) and decides the band A sign-in method (MR-I6) | MR-G6, I6 |
| T020 | KK-40 | S15 | The penetration test also covers bypassing consent or verification, bypassing band rules (a band A account reaching free text) and access to duels in another class | MR-C1, T1, S3 |

**E03 Telemetry and warehouse**

| Ticket | Jira | Sprint | Change | Rules |
| --- | --- | --- | --- | --- |
| T023 | KK-43 | S2 | In review; follow-up in NEW-7. Changes: a list of allowed events per band; `track_id` (Bac section) replaced by the grade level; `Activity.MOCK_BAC` replaced by exam practice; retention per MR-D9; `response.expression` limited to maths grammar. Keep the existing ban on field names such as `age` and `birth_date` | MR-D1–D3, D9 |
| T024 | KK-44 | S3 | The SDK applies the band's allowed-event list (no `item.interaction` or `item.hesitation` for band A). Instead of "respects Do-Not-Track for non-essential events", non-essential events are off by default for every pupil | MR-D2, D5 |
| T025 | KK-45 | S4 | Ingestion rejects events not allowed for the token's `age_band`, drops "enriches with geo" for everyone, and checks the expression grammar | MR-D3, D7 |
| T026 | KK-46 | S4 | Leaderboard sorted sets exist only per class; no national keys | MR-S1, S2 |
| T030 | KK-50 | S6 | No engagement-risk or send-time features for pupils | MR-P2, N5 |
| T191 | KK-211 | S8 | Band A: aggregate counts only. Minimum group size of 10. No individual funnels | MR-D6 |
| T192 | KK-212 | S13 | Aggregated dashboards with small groups suppressed; no KPIs per pupil | MR-D6 |
| T219 | KK-239 | S5 | Synthetic pupils aged 11–15, parents with declared capacities, consent states, band changes, and school and direct channels | MR-R5 |

**E05, E06 Brain and routing**

| Ticket | Jira | Sprint | Change | Rules |
| --- | --- | --- | --- | --- |
| T047 | KK-67 | S9 | Fairness slices by band and grade; features that fail the gate stop being collected (MR-D2), not just unused | MR-P6, D2 |
| T049 | KK-69 | S9 | Child-friendly explanations; band A shows states, not probabilities; a way to ask for a human review or a reset | MR-P3, P4 |
| T055 | KK-75 | S10 | DPO approval for each experiment; parents informed; no engagement experiments on band A; the article 49 question settled before the first experiment | MR-P2, X2 |
| T057 | KK-77 | S11 | Shorter default sessions for band A (product scope from Bac weights to 6e–9e is outside this draft) | MR-N6 |
| T187 | KK-207 | S15 | No predicted score for band A. For band B, optional and off by default, shown only to the pupil and parent, never to teachers or schools as a ranking, never used for admission | MR-P1, P3 |

**E07, E08 LLM gateway and tutor**

| Ticket | Jira | Sprint | Change | Rules |
| --- | --- | --- | --- | --- |
| T059 | KK-79 | S5 | Only providers that meet MR-T6. Routing by band (no pupil free text for band A). Requests carry no pupil or tenant identifiers. Real traffic only after the transfer is authorised | MR-T6, R3 |
| T062 | KK-82 | S7 | The judge also checks age appropriateness and reading level by grade | MR-T5 |
| T064 | KK-84 | S8 | Band A cache keys use request IDs. Band B caches only filtered, normalised questions, never raw pupil text | MR-T2, T3 |
| T066 | KK-86 | S9 | A child-specific red-team set: grooming, eliciting personal data, self-harm, sexual content, persuading the tutor to act as a companion | MR-T4, G6 |
| T223 | KK-243 | S9 | Test set in children's language (11–15) in French, Arabic and Tunisian Arabic. Band A relies on the help button (NEW-9). Escalation never notifies a parent automatically when the family may be involved | MR-G2, G3 |
| T069 | KK-89 | S8 | **Rewrite** by band: band A gets the guided tutor (NEW-4); band B gets free text about the item, up to 300 characters, with the filter (NEW-5) and 30-day retention. AI disclosure on every conversation. Change "Tutor conversation persists across reloads" to "persists for 30 days (band B) or as request and hint IDs only (band A)" | MR-T1–T4, T9 |
| T070 | KK-90 | S8 | The hint ladder works without any LLM (authored hints), for families who refuse the tutor consent | MR-T8 |
| T072 | KK-92 | S9 | Adds a "ça m'a mis mal à l'aise" option routed to the safeguarding lead | MR-G2 |
| T073 | KK-93 | S14 | Band A: on-device recognition only. Band B: server fallback only with the tutor consent | MR-T7 |
| T074 | KK-94 | S9 | Glossary and reading level for 6e–9e | MR-T5 |
| T075 | KK-95 | S13 | Becomes the main progress channel for band A parents. No comparison with other pupils (already a criterion) | MR-F1 |
| T144 | KK-164 | S13 | Simplified-language (FALC) levels mapped to grades | MR-T5 |

**E10 Engagement and gamification**

| Ticket | Jira | Sprint | Change | Rules |
| --- | --- | --- | --- | --- |
| T084 | KK-104 | S12 | **Rewrite and split** (13 points): band A only teacher-run class battles and bot practice; band B duels with classmates or friends added by in-person code; no open matchmaking, no chat, no outside spectators; block and report. Replace the criterion "5,000 concurrent battles" with class-scale load and a cross-class isolation test | MR-S3 |
| T087 | KK-107 | S9 | Band A: weekly goals, no daily streaks. Band B: optional streaks with freezes; no notifications about streaks | MR-S5 |
| T088 | KK-108 | S11 | **Rescope**: no national or school leaderboards; class only, under nicknames, off by default, band B only; band A gets shared class goals | MR-S1, S2 |
| T089 | KK-109 | S10 | Quiet hours by band; no SMS or email to pupils | MR-N1, N2 |
| T090 | KK-110 | S13 | **Drop, or rescope** to reminder rules approved by the parent, with no churn-risk model | MR-P2, N4 |
| T091 | KK-111 | S14 | Certificates private by default; minimal public verification page; link expiry; sharing controlled by the parent | MR-S6, S7 |

**E11 Portals and multi-tenancy**

| Ticket | Jira | Sprint | Change | Rules |
| --- | --- | --- | --- | --- |
| T093 | KK-113 | S12 | Pupil CSV import only when NEW-1 confirms the route (Kuizi as processor and the school's lawful basis). Otherwise class codes and parent enrolment. The criterion "Students receive activation + parent-consent flow automatically" changes to "Parents receive the enrolment and consent flow" | MR-E1, E2 |
| T094 | KK-114 | S14 | School-managed pupil accounts only where counsel accepts them; no consumer Google accounts for band A | MR-I2 |
| T095 | KK-115 | S13 | Teachers' view minimised (MR-E3); live feed only during a class session; no disengagement alerts based on home use for band A | MR-E3, E4 |
| T096 | KK-116 | S14 | **Rewrite**: no flags accusing an individual of cheating or collusion. Aggregated integrity signals per test; human review, explanation, a way to contest, no automatic sanction | MR-P5 |
| T097 | KK-117 | S14 | Becomes the control centre for band A. Screen-time and bedtime controls. A panel for the child showing what parents see, and an indicator when controls are on. Band B privacy limits. The objection flow | MR-F1–F4, N6 |
| T224 | KK-244 | S9 | Band A: the parent completes the class join. Teachers see the first name and initial | MR-E2, I4 |
| T225 | KK-245 | S13 | The assignment reminder goes to the child's device only if allowed; otherwise to the parent | MR-N1 |
| T226 | KK-246 | S15 | Rules for private notes (no health, discipline or family content; parent access; deleted at year end). Sharing of accommodations by band | MR-E5, A3 |
| T227 | KK-247 | S16 | Band A pupils receive announcements in the app only | MR-N1 |
| T100 | KK-120 | S16 | Aggregated reports; no individual rankings | MR-S1 |
| T228 | KK-248 | S16 | At year-end rollover, data of pupils who left is deleted on the retention schedule | MR-R1 |

**E12 Quality and release**

| Ticket | Jira | Sprint | Change | Rules |
| --- | --- | --- | --- | --- |
| T102 | KK-122 | S12 | End-to-end tests for both bands, and for the move between bands | MR-C9 |
| T108 | KK-127 | S12 | The pilot starts only after NEW-1, NEW-6, NEW-10, NEW-11 and NEW-12, the article 28 condition, the transfer authorisations and the Ministry question are settled | MR-C1, R3, E8, X1 |

**E14 Accessibility**

| Ticket | Jira | Sprint | Change | Rules |
| --- | --- | --- | --- | --- |
| T134 | KK-154 | S4 | Stores settings, not diagnosis labels; the parent manages the profile for band A | MR-A4, A3 |
| T135 | KK-155 | S6 | Presets named by what they do, not by condition (the current preset names include "dyslexia" and "attention") | MR-A4 |
| T143 | KK-163 | S13 | Band A has no leaderboards or duels at all; calm mode still hides timers | MR-S2, S3 |
| T146 | KK-166 | S13 | Who shares accommodations depends on the band | MR-A3 |
| T150 | KK-170 | S13 | Co-design with children follows NEW-11 (consent, assent, safeguarding) | MR-X1 |
| T151 | KK-171 | S11 | Adds the article 62–63 analysis and the article 28 condition for health data | MR-A1, A2 |
| T141 | KK-161 | S11 | On-device dictation for band A | MR-T7 |

**E15 Focus and notifications**

| Ticket | Jira | Sprint | Change | Rules |
| --- | --- | --- | --- | --- |
| T152 | KK-172 | S10 | Quiet hours and budgets by band in the policy; push to the child's device off by default for band A | MR-N1–N3 |
| T154 | KK-174 | S14 | **Drop, or rescope** to class-level default windows with no individual profiling | MR-N5, P2 |
| T155 | KK-175 | S11 | No 45-minute option for band A | MR-N7 |
| T157 | KK-177 | S13 | The parent controls band A's settings. Band B maximum of 3 a day, not 5 | MR-N1 |
| T159 | KK-179 | S14 | The Bac calendar becomes the school calendar (product). No extra reminders to band A before exams | MR-N1 |
| T161 | KK-181 | S14 | Adds a metric: zero sends to children's devices outside allowed windows, per band | MR-N2 |
| T196 | KK-216 | S14 | Lifecycle messages go to parents only, with consent; nothing to pupils | MR-N4 |
| T229 | KK-249 | S13 | A child's device registers for push only if allowed | MR-N1 |

**E16 Native apps and store compliance**

| Ticket | Jira | Sprint | Change | Rules |
| --- | --- | --- | --- | --- |
| T163 / T164 | KK-183 / KK-184 | S7 / S8 | No third-party analytics SDKs; a parental gate in front of links out and purchases | MR-D5, M3 |
| T166 | KK-186 | S7 | **Rescope**: no Apple or Google sign-in for pupils. If Google sign-in is offered to parents, guideline 4.8 applies | MR-I2 |
| T167 | KK-187 | S8 | A pupil's deletion request is honoured and the parent is told (counsel to confirm) | MR-C7, F4 |
| T168 | KK-188 | S15 | Purchases only from the parent account or behind a parental gate | MR-M3 |
| T169 | KK-189 | S15 | Adds: the Kids Category decision (Apple 1.3), the Google Play Families target audience, the age rating, and Data safety answers that match the band rules. Suggest 3 → 5 points | MR-D5, M1 |
| T170 | KK-190 | S15 | No Live Activities for duels in band A; nothing personal on the lock screen | MR-N8 |
| T230 | KK-250 | S9 | Crash reporting with no device identifiers and no personal data; the vendor has a DPA and an authorised transfer | MR-D5, R3 |

**E17 Learner experience**

| Ticket | Jira | Sprint | Change | Rules |
| --- | --- | --- | --- | --- |
| T175 | KK-195 | S7 | Choose the grade (6e–9e) instead of the Bac section. Consent and assent come before the placement test | MR-C1, C6 |
| T176 | KK-196 | S12 | Band A: no failure probabilities and no estimated grade; "concepts to review" instead | MR-P3 |
| T177 | KK-197 | S11 | Band A: concept states, no percentages for predicted success | MR-P3 |
| T180 | KK-200 | S14 | No national or school scope; class leaderboard for band B only, opt-in | MR-S1, S2 |
| T181 | KK-201 | S13 | Follows the T084 rewrite | MR-S3 |
| T182 | KK-202 | S13 | Shows which settings the parent controls; band-specific settings | MR-F3 |
| T183 | KK-203 | S13 | Testing with children follows NEW-11 | MR-X1 |
| T209 | KK-229 | S10 | The pupil cannot unlink the parent. Display name is a first name or generated nickname; no photo upload | MR-I4 |

**E19 Growth and go-to-market**

| Ticket | Jira | Sprint | Change | Rules |
| --- | --- | --- | --- | --- |
| T193 | KK-213 | S14 | The marketing site addresses parents and schools, not children | MR-M2 |
| T194 / T195 | KK-214 / KK-215 | S16 | Checkout and plans for parents only; free-plan limits never used to pressure children | MR-M3 |
| T197 | KK-217 | S17 | Store screenshots without real children; ratings prompts shown only to parents | MR-M2 |
| T198 | KK-218 | S14 | No NPS or free-text feedback from band A (ask parents); limited free text for band B, with a personal-data warning | MR-D6, T2 |
| T199 | KK-219 | S16 | Claims about learning outcomes made to parents need evidence | MR-M4 |
| T200 | KK-220 | S15 | No marketing to pupils in schools; depends on NEW-10 | MR-M2, E8 |

**E20 Back office and legal**

| Ticket | Jira | Sprint | Change | Rules |
| --- | --- | --- | --- | --- |
| T201 | KK-221 | S12 | Staff may impersonate a pupil account only for a safeguarding or support need, with a recorded reason and the parent informed afterwards (counsel to confirm). Always audited | MR-G5, E7 |
| T203 | KK-223 | S13 | Safeguarding escalations go in a separate queue that only the safeguarding lead can open | MR-G4 |
| T204 | KK-224 | S16 | Help articles for children, written for each band | MR-F3 |
| T205 | KK-225 | S16 | The parent's identity is checked before acting on a child's account; no support chat directly with band A children | MR-F1 |
| T207 | KK-227 | S10 | Privacy notices for each band and for parents in French and Arabic (section 7 as a starting point); article 31 content; the school DPA follows the role model in NEW-1 | MR-C8, E1 |
| T208 | KK-228 | S15 | Teacher training covers these rules and safeguarding | MR-G1 |
| T216 | KK-236 | S16 | The law sets no notification deadline (section 2.2), so counsel sets one (good practice: 72 hours). Plain-language messages for parents and children | Q12 |
| T222 | KK-242 | S6 | Scope 11–15. Child Protection Code art. 31 route to the délégué; helplines confirmed; a rule for concerns involving the family; staff vetting | MR-G1–G5 |
| T236 | KK-256 | S6 | Adds the minors terms of the LLM providers (OpenAI zero data retention for under-13s, Anthropic's requirements), article 22 checks of processors, and the transfer authorisations from NEW-6 | MR-T6, R3, R4 |

**E01 Platform**

| Ticket | Jira | Sprint | Change | Rules |
| --- | --- | --- | --- | --- |
| T240 | KK-260 | S11 | Blocked by NEW-6: pupils' personal data moves abroad only once authorised | MR-R3 |

### 5.3 Product scope changes outside this draft

The move from the Bac to 6e–9e also changes curriculum and exam tickets, with no legal content: T033 (subject and track), T035, T038, T039, T044, T111–T132 (E13 subject expansion), T184–T190 (E18: the Bac becomes school exams and the 6e and 9e entrance exams), T145 (the "mock Bac" becomes exam practice), T057, T054 and T159 (exam calendars), and T233. T160 (parent notifications) needs no change; it becomes the main notification channel for band A. One observation for the product-curriculum agent: in basic education, maths and sciences are taught in **Arabic** [Unconfirmed]. That makes Arabic the main content language for 11–15, which matters for "age-appropriate application" (AADC 3).

### 5.4 Documents to reconcile (main session)

- **Conflicts with `accessibility-focus-notifications.md`.** These need a product-owner decision before that document changes:
  - FR-N3 quiet hours (22:00–07:00) against MR-N2;
  - FR-N4 budget (2 a day) against MR-N1;
  - FR-N5 per-student send time against MR-N5;
  - FR-N7 exam ramp against MR-N1;
  - FR-P3 the student alone decides sharing, against MR-A3 for band A;
  - FR-F1 45-minute sessions against MR-N7;
  - section 3 "24-month telemetry rule" against MR-D9;
  - FR-A8 dictation against MR-T7.
- **Text that still says "Bac, 17–19":**
  - `README.md`, `CLAUDE.md` (first line), `docs/product/overview.md`;
  - `docs/dev/identity.md` (role table, Google sign-in for students);
  - `docs/data/event-catalogue.md` and `schemas/events/catalogue.yaml` (`track_id`, `MOCK_BAC`, retention);
  - the introduction of `docs/backlog/APL_Full_Backlog.md` (through `tools/backlog/additions.py`);
  - every role brief in `.claude/agents/`.
- **Decisions page.** `docs/product-owner-decisions.md` should list the *(proposal)* defaults of section 4 and the counsel questions of section 6.

### 5.5 New tickets

Points and sprints are suggestions for the main session.

**NEW-1. Counsel's opinion on the lawful route for processing pupils' data (11–15) under Law 2004-63**
Legal / DPO with outside counsel · 3 points · S3 · blocks T013 (close), T017, T093, T236, T240.
*Why:* article 28 (tutor's consent and the family judge's authorisation) applies to every pupil and carries criminal penalties (art. 87, 101). The route chosen (a judge's authorisation, or public schools under art. 53–57) shapes consent, onboarding, contracts and hosting.

- A written opinion signed by Tunisian counsel answers Q1–Q11 and Q23 (section 6), quoting the articles relied on.
- The chosen route is recorded as a product-owner decision (ADR or decisions page), with the steps, the responsible person and an estimated time for each authorisation.
- T013, T017, T093, T207 and T236 have their acceptance criteria updated to match the opinion, in the backlog and in Jira.

**NEW-2. Age bands in identity and one policy table for band rules**
Backend · 5 points · S4 · blocked by T012 · blocks every feature that depends on the band.
*Why:* rules differ between bands A and B and must be enforced the same way everywhere, using a coarse band rather than a birth date.

- The band is derived from the parent-declared birth month and year and stored only as a band plus its change date. Tokens carry `age_band` and never a birth date (test on real tokens from the local Keycloak).
- Every band-dependent feature reads one policy table (`MR-*` rules). Tests cover each feature in each band, and a feature missing from the table fails CI.
- When a pupil turns 13, the band changes on the first day of the following month, the pupil and parent are told in French and Arabic, and new band B features stay off until they are switched on.

**NEW-3. Child-facing privacy information and assent screens, plus the parent notice**
Design / UX with Legal / DPO · 3 points · S5 · blocked by NEW-1 · blocks T013 (assent), T207.
*Why:* the parent must receive the article 31 information in written form; children have a right to be heard (Child Protection Code art. 10) and to transparency (AADC 4).

- Band A screens use pictograms and audio, and band B screens use short text, in French and Arabic (right to left). Both pass WCAG 2.2 AA, and children of each band understand them in the usability round (T183): at least 8 of 10 can explain what Kuizi keeps.
- The parent notice lists every article 31 item, and the policy version is recorded with each consent.
- The pupil's assent (band A "J'ai compris"; band B agreement) is stored with its version, and a "pas maintenant" keeps the account inactive.

**NEW-4. Guided tutor for band A (no free text)**
LLM / Applied AI with Frontend · 5 points · S8 · blocked by T069, NEW-2.
*Why:* children under 13 should not have an open chat with an AI, and their text should never reach an LLM (MR-T1, OpenAI terms).

- No free-text input can be reached with a band A token: the server rejects free-text payloads (test).
- Suggested requests (at least "je ne comprends pas", "un indice", "un exemple semblable") and the maths keypad cover the hint ladder in French and Arabic. In the usability round, at least 8 of 10 band A pupils get help without asking for a text box.
- For band A, only request and hint IDs are stored; a store audit finds no conversation text for band A accounts.

**NEW-5. Personal-data filter and 30-day retention for band B tutor text**
LLM / Applied AI · 5 points · S8 · blocked by T069, T059.
*Why:* pupils' free text can contain personal data that would otherwise go to a foreign provider (art. 11, 52).

- On a labelled set of 500 messages in French, Arabic and Tunisian Arabic, at least 98 % of names, phone numbers, emails, addresses and CIN-like numbers are removed before leaving Kuizi.
- Gateway logs show no pupil ID, tenant ID or name in any provider request (automated check).
- Band B conversation text is deleted 30 days after the last message (automated test), and is excluded from every training set.

**NEW-6. Data residency and cross-border transfers for children's data (ADR)**
Platform / DevOps with Legal / DPO · 3 points · S5 · blocked by NEW-1 · blocks T240, T236, real traffic on T059.
*Why:* every transfer of pupils' data abroad needs INPDP authorisation requested through the family judge (art. 52), and the INPDP has objected to foreign hosting of pupils' data.

- An ADR compares hosting in Tunisia with AWS Paris plus authorisation, covering legal steps, delays, cost and the effect on ADR 0006 and T240. The product owner decides.
- A data-flow map lists every flow out of Tunisia (vendor, data, purpose, legal basis, authorisation status), kept up to date in T236.
- Until a flow is authorised, configuration blocks pupils' personal data from reaching it (a test in the cloud move, T240).

**NEW-7. Telemetry policy by band: catalogue, SDK and ingestion**
Data Engineering · 5 points · S4 · blocked by T023, NEW-2 · blocks closing T024 and T025.
*Why:* data minimisation by band (MR-D1 to MR-D9) must be in the contracts and enforced on the server.

- `schemas/events/catalogue.yaml` states for each event which bands may send it and its retention per band, and the generated catalogue shows both. `make schemas-check` fails on an event with no band rule.
- Ingestion drops events not allowed for the token's band and counts them. A test shows `item.interaction` and `item.hesitation` from band A are rejected.
- `response.expression` accepts only the maths keypad grammar, and ingestion rejects other text (test with letters, emails and phone numbers).

**NEW-8. Safe identity display: generated nicknames and preset avatars**
Frontend with Backend · 3 points · S9 · blocks T088, T084, T224.
*Why:* names and photos expose children, and free-text nicknames invite bullying and personal data (MR-I4).

- Nicknames are generated from word lists in French and Arabic. Native speakers review the lists, and a test rejects offensive combinations.
- No API accepts a free-text display name or a photo for a pupil (tests).
- Other pupils only ever see the nickname and a preset avatar (test across leaderboards, duels and class battles).

**NEW-9. "J'ai besoin d'aide" button and helplines on every pupil screen**
Frontend · 3 points · S9 · blocked by T222 · blocks T108.
*Why:* children need a way to get help that works without free text (Child Protection Code art. 32; MR-G2).

- The button can be reached in at most 2 taps from every pupil screen, in French and Arabic, with touch targets of at least 44 px, and works with a screen reader.
- It shows the helplines and emergency numbers confirmed in T222, and they can be changed without releasing a new app version.
- The optional "un adulte de mon école peut me contacter" reaches the safeguarding lead within 15 minutes and stores no text for band A (test).

**NEW-10. School-use file and the role model in school contracts**
Legal / DPO · 3 points · S6 · blocked by NEW-1 · blocks T093, T108, T200.
*Why:* using Kuizi in public schools may need Ministry of Education authorisation (Q15). The controller and processor roles decide whether a school can share pupil lists (art. 44, 47, 57).

- A file in French and Arabic (description, summary of the impact assessment, consent model, hosting), reviewed by counsel, is ready for the product owner. The agent never sends it.
- The school DPA template states the roles chosen in NEW-1 and forbids using Kuizi data for orientation, admission or discipline (MR-P1).
- The product owner's decision on whether and when to approach the Ministry is recorded.

**NEW-11. Protocol for research and testing with children**
Legal / DPO with Design / UX · 2 points · S8 · blocks T183, T150, T108.
*Why:* usability rounds, co-design and the pilot involve real children (MR-X1).

- Counsel or the DPO approves the protocol, which covers consent, the article 28 condition, assent, two adults present, recording rules and deletion.
- Templates for the parent's consent and the child's assent exist in French and Arabic (right to left, plain language).
- A pre-session checklist blocks any session where a consent or assent is missing.

**NEW-12. Access policy and vetting for people who handle children's data**
Legal / DPO with Customer Success & Support · 2 points · S6 · blocks T201, T203, T205, T108.
*Why:* confidentiality (art. 23), the article 22 conditions for agents, and the safeguarding duty (Child Protection Code art. 31).

- Everyone with access to pupils' data has signed a confidentiality undertaking and completed the vetting counsel requires before being given access.
- Access is reviewed every quarter and limited by role. Safeguarding records can be opened only by the safeguarding lead (audit test).
- Safeguarding training is completed before access is given (records kept).

## 6. Open legal questions for counsel

These are not answered in this draft. The product owner passes them to counsel; the agent does not contact anyone.

| # | Question | Articles |
| --- | --- | --- |
| Q1 | How is the family judge's authorisation under article 28 obtained in practice for an online learning service: per child, per controller, or as a general authorisation? From which court, in what form, with what evidence, and how long does it take? Is there INPDP or court practice? Does a contract signed by the parent (art. 29) change anything? | 2004-63 art. 28, 29 |
| Q2 | If a public school, a regional directorate or the Ministry (CNTE) is the controller and Kuizi its processor, do the exemptions in articles 53–54 (from articles 27 and 28) cover adaptive learning in class and at home? What instrument is needed? Does article 57 stop a public school from giving pupil lists to Kuizi even as a processor, since a processor is not a "tiers" under article 6? | art. 6, 53, 54, 57 |
| Q3 | The same question for private schools, under article 47 | art. 47, 28 |
| Q4 | Who is the "tuteur" whose consent counts (father; mother with custody for studies)? Is one parent enough? How should separated or disagreeing parents be handled, and can Kuizi ask for proof of capacity? | Code of Personal Status art. 154, 67 [Unconfirmed]; 2004-63 art. 28, 43 |
| Q5 | Does an electronic consent (code sent by SMS plus a recorded click) meet "consentement exprès et écrit" and "trace écrite"? Is an electronic signature needed (Law 2000-83)? | 2004-63 art. 27, 14, 31 |
| Q6 | Must the article 31 information be given at least one month before processing starts, for every new pupil? | art. 31 |
| Q7 | What weight does a 13–15-year-old's refusal or withdrawal carry ("la personne concernée … peut se rétracter")? Can a child of any age withdraw against the tutor's wish? | art. 27 para. 2; Child Protection Code art. 10, 40, 42 |
| Q8 | Do the article 22 conditions (Tunisian nationality, residence in Tunisia, no criminal record) apply to Kuizi's legal representative, to foreign processors (AWS, LLM providers, Snowflake, Datadog) and to their staff? How does the INPDP apply them? | art. 22, 8 |
| Q9 | Which flows count as transfers of personal data (pseudonymous telemetry, filtered LLM prompts)? Can one request to the family judge cover a whole flow? Will the INPDP authorise hosting in the EU? Does the 5 November 2020 hosting circular (number unconfirmed) bind private providers serving public schools? | art. 50–52, 90 |
| Q10 | Are accommodation flags health data, and if so does article 63 (processing only by doctors or people bound to professional secrecy) apply? Is an INPDP authorisation needed for them? | art. 14, 15, 62–65 |
| Q11 | How does the article 45 requirement (a bailiff's report with an INPDP expert) apply to routine automated deletions and erasure requests? | art. 45, 94 |
| Q12 | The law has no breach-notification article. What notifications to the INPDP, schools and parents does counsel recommend, and within what time? | art. 18, 19; Convention 108+ |
| Q13 | Does the INPDP expect anything specific for knowledge tracing of children: prior consultation, an authorisation, limits? | art. 9, 11, 76 |
| Q14 | Are pedagogical A/B tests "scientific research" needing consent and INPDP authorisation? | art. 49, 66–68 |
| Q15 | Must the Ministry of Education authorise Kuizi's use in public schools, and contacts between Kuizi and schools? Are there circulars on ed-tech or on pupils' data? | — |
| Q16 | Does the article 31 duty to report bind Kuizi as a company and its staff for concerns learnt online? Are Kuizi's moderators and safeguarding lead "personnes chargées de la protection" (so that reporting every situation is mandatory)? | Child Protection Code art. 20, 31–34 |
| Q17 | How should the tutor's right of access (art. 32) be balanced with the child's privacy (Child Protection Code art. 6) for band B tutor text? | 2004-63 art. 32; Child Protection Code art. 6 |
| Q18 | Are any rules different for pupils of 16–17 in these grades? | 2004-63 art. 28; Child Protection Code art. 3 |
| Q19 | What is needed to use images of children in marketing or store screenshots? (A 2025 statement attributed to child-protection officials says the tutor and the family judge must both agree [Unconfirmed].) | art. 28 |
| Q20 | How long must consent records, safeguarding records and audit logs be kept, given limitation periods? | art. 45, 64 |
| Q21 | What is the status of the 2025 draft organic law, and its rules for children and transition? Should Kuizi design for it now? | — |
| Q22 | Has Tunisia ratified Convention 108+? | CETS 223 |
| Q23 | Confirm the complete list and order of formalities (declaration, decree 2007-3004, authorisations under art. 15, 49 and 52, the family judge under art. 28 and 52), and check this draft against the official consolidated texts of Law 2004-63 and the Child Protection Code | art. 7, 8, 15, 28, 49, 52 |
| Q24 | Is any parent-verification method acceptable for band A in the direct channel, without a school? | art. 28; MR-C3 |

## 7. Plain-language summaries (draft product copy)

> **DRAFT copy.** Written from this draft's rules, which counsel has not approved. It needs native-speaker review (French and Tunisian Arabic), a test with children (T183) and the brand's decisions on forms of address and gender-neutral Arabic. The Arabic uses neutral or impersonal forms where possible. Numbers in brackets are placeholders until T222 confirms them.

### 7.1 Pupils, 11–12 years old

**Français**

- Kuizi t'aide à réviser les maths et les sciences, exercice après exercice.
- Tes parents ont dit oui pour que tu utilises Kuizi. Ton avis compte aussi : tu peux dire « pas maintenant ».
- Kuizi garde tes réponses pour choisir le prochain exercice. Se tromper, c'est apprendre.
- Tu n'écris pas de messages. Tu choisis l'aide dont tu as besoin : un indice ou un exemple.
- Pas de publicité dans Kuizi, et personne n'achète tes informations.
- Ton enseignant voit ce que tu as appris. Tes parents voient tes progrès. Tu peux voir ce qu'ils voient.
- Si quelque chose te fait peur ou te rend triste : appuie sur « J'ai besoin d'aide », parle à un adulte de confiance ou appelle le [1809], c'est gratuit.
- Tu peux arrêter quand tu veux. Tes parents peuvent supprimer ton compte.

<div dir="rtl" lang="ar">

**العربية**

- كويزي يساعد على مراجعة الرياضيات والعلوم، تمرينًا بعد تمرين.
- لا يُستعمل كويزي إلّا بعد موافقة الوليّ. ورأي التلميذ مهمّ أيضًا: يمكن أن يكون الجواب «ليس الآن».
- يحفظ كويزي الإجابات ليختار التمرين الموالي. الخطأ جزء من التعلّم.
- لا توجد كتابة رسائل: يُختار نوع المساعدة المطلوبة، مثل تلميح أو مثال مشابه.
- لا إشهار في كويزي، ولا تُباع المعلومات لأيّ جهة.
- يرى المعلّم ما تمّ تعلّمه، ويرى الوليّ التقدّم، ويمكن للتلميذ أن يرى ما يرونه.
- عند الخوف أو الحزن: زرّ «أحتاج إلى مساعدة»، أو الحديث مع شخص كبير موثوق، أو الاتصال بالرقم [1809] مجّانًا.
- يمكن التوقّف في أيّ وقت، ويمكن للوليّ حذف الحساب.

</div>

### 7.2 Pupils, 13–15 years old

**Français**

- Tes parents ont donné leur accord ; on te demande aussi le tien.
- Kuizi utilise tes réponses pour adapter les exercices, et seulement pour t'aider à apprendre : pas de publicité, pas de vente de tes données.
- Tu peux poser des questions au tuteur sur un exercice. Le tuteur est une intelligence artificielle, pas une personne. N'écris jamais ton nom, ton adresse ou ton numéro de téléphone.
- Tes messages au tuteur sont effacés après 30 jours. Tes parents et ton enseignant ne les lisent pas, sauf si ta sécurité est en danger.
- Classements et duels : seulement avec ta classe, avec un pseudo, et seulement si tu les actives.
- Tu choisis quels aménagements ton enseignant peut voir.
- Tu peux voir ce que voient tes parents et ton enseignant, demander une copie de tes données ou demander leur suppression.
- Besoin d'aide ? Bouton « J'ai besoin d'aide », un adulte de confiance, ou le [1809].

<div dir="rtl" lang="ar">

**العربية**

- وافق الوليّ، ونطلب أيضًا موافقة التلميذ.
- تُستعمل الإجابات لتكييف التمارين، وللتعلّم فقط: لا إشهار ولا بيع للمعطيات.
- يمكن طرح أسئلة على المرافق حول التمرين. المرافق ذكاء اصطناعي وليس إنسانًا. يُرجى عدم كتابة الاسم أو العنوان أو رقم الهاتف.
- تُحذف الرسائل الموجّهة إلى المرافق بعد 30 يومًا. لا يقرؤها الوليّ ولا المعلّم، إلّا إذا كانت السلامة في خطر.
- الترتيب والمبارزات: داخل القسم فقط، باسم مستعار، وبعد التفعيل فقط.
- يختار التلميذ التسهيلات التي يمكن للمعلّم رؤيتها.
- يمكن الاطّلاع على ما يراه الوليّ والمعلّم، وطلب نسخة من المعطيات أو حذفها.
- عند الحاجة إلى مساعدة: زرّ «أحتاج إلى مساعدة»، أو شخص كبير موثوق، أو الرقم [1809].

</div>

### 7.3 Parents and tutors

**Français**

- Kuizi traite les données de votre enfant dans un seul but : l'aider à apprendre.
- Le compte n'est activé qu'après votre accord exprès et écrit. [D'autres conditions légales propres aux enfants sont en cours de vérification : à compléter après l'avis juridique.]
- Ce que nous collectons : prénom, classe et niveau, mois et année de naissance, réponses aux exercices, réglages. Nous ne collectons pas : photo, adresse, téléphone de l'enfant, numéro de carte d'identité.
- Pas de publicité, pas de vente de données, pas de profilage commercial.
- Accords séparés, que vous pouvez refuser sans perdre l'essentiel du service : aménagements (données sensibles), tuteur à intelligence artificielle, notifications sur l'appareil de l'enfant.
- L'enseignant voit seulement la progression par notion et les devoirs rendus.
- Durées de conservation et hébergement : [à compléter après validation par le DPO].
- Vos droits : accès et copie sous un mois, rectification, opposition, retrait de votre accord à tout moment, et réclamation auprès de l'Instance nationale de protection des données à caractère personnel (INPDP).

<div dir="rtl" lang="ar">

**العربية**

- يعالج كويزي معطيات طفلكم لغرض واحد: مساعدته على التعلّم.
- لا يُفعَّل الحساب إلّا بعد موافقتكم الصريحة والكتابية. [شروط قانونية أخرى خاصّة بالأطفال قيد التثبّت: تُستكمل بعد الرأي القانوني.]
- ما نجمعه: الاسم الأوّل، القسم والمستوى، شهر الولادة وسنتها، الإجابات على التمارين، الإعدادات. ما لا نجمعه: الصورة، العنوان، رقم هاتف الطفل، رقم بطاقة التعريف.
- لا إشهار، ولا بيع للمعطيات، ولا تحليل لأغراض تجارية.
- موافقات منفصلة يمكن رفضها دون فقدان الخدمة الأساسية: التسهيلات (معطيات حسّاسة)، المرافق بالذكاء الاصطناعي، الإشعارات على جهاز الطفل.
- يرى المعلّم التقدّم في المفاهيم وإنجاز الواجبات فقط.
- مدّة الحفظ ومكان الاستضافة: [تُستكمل بعد مصادقة المسؤول عن حماية المعطيات].
- حقوقكم: النفاذ والحصول على نسخة في أجل شهر، التصحيح، الاعتراض، سحب الموافقة في أيّ وقت، وتقديم شكوى إلى الهيئة الوطنية لحماية المعطيات الشخصية.

</div>

## 8. Sources

Tunisian texts (read for this draft):

- [Loi organique n° 2004-63 du 27 juillet 2004](https://legislation-securite.tn/wp-content/uploads/sites/5/2023/11/Loi-n°-2004-63-du-27-Juillet-2004-Fr.pdf), French text, DCAF database of Tunisian security-sector legislation (consolidated copy, not the JORT).
- [Le Code de la protection de l'enfant, annotated edition](https://www.unicef.org/tunisia/media/8551/file/Tunisia_Appendix_2_EUSurvey.pdf.pdf), Ministry of Women, Family and Children and UNICEF (Kotrane and Khemakhem).
- [AHJUCAF, Tunisia: answers on minors](https://www.ahjucaf.org/sites/default/files/inline-files/AHJUCAF%20Dakar%20PP%20Guediri%20Tunisie%20Re%CC%81ponse%20aux%20mineurs.pdf) (capacity from 13; Penal Code art. 43), secondary source.

Tunisian context (secondary sources):

- [Acteurs publics, 3 September 2021: INPDP and the Ministry of Education's use of Google Forms](https://acteurspublics.fr/articles/polemique-en-tunisie-sur-lutilisation-dune-plate-forme-pour-un-sondage-du-ministere-de-leducation)
- [Business News, 27 February 2026: 2025 draft organic law on personal data](https://businessnews.com.tn/?p=1390118); [AllAfrica, August 2025](https://fr.allafrica.com/stories/202508050456.html)
- [Tuniscope, 6 May 2026: the 1809 line](https://www.tuniscope.com/article/431127/societe/actualites/le-ministere-de-la-famille-de-la-femme-de-l-enfance-et-des-personnes-agees-105514); [Kapitalis, 9 August 2025: 192 and 1809](https://kapitalis.com/tunisie/2025/08/09/25-000-cas-denfants-en-danger-signales-chaque-annee-en-tunisie/); [UNICEF Tunisia](https://www.unicef.org/tunisia/il-grandira-mais-il-noubliera-pas)
- [La Presse, 20 November 2025: the duty to report under the Child Protection Code](https://www.lapresse.tn/?p=1651971)
- [Managers, 30 March 2026: the Ministry's free tutoring platform](https://managers.tn/2026/03/30/une-premiere-nationale-la-tunisie-lance-sa-plateforme-officielle-de-soutien-scolaire-gratuite-du-primaire-jusquau-baccalaureat/); [AllAfrica, July 2026: "Vie scolaire"](https://fr.allafrica.com/stories/202607280218.html)

International:

- [Council of Europe: Welcome Tunisia, new party to Convention 108](https://www.coe.int/en/web/data-protection/home/-/asset_publisher/RMbj8Pk1ApgJ/content/welcome-tunisia-new-party-to-convention-108)
- [Acteurs publics: Tunisia signs Convention 108+](https://acteurspublics.fr/articles/la-tunisie-signe-la-convention-108-sur-la-protection-des-donnees-personnelles/); [African Manager, May 2019](https://africanmanager.com/la-tunisie-sengage-et-cette-fois-cest-du-serieux/)
- [Council of Europe: Greece and Monaco ratify Convention 108+ (32nd and 33rd)](https://www.coe.int/en/web/data-protection/-/greece-becomes-the-32nd-and-monaco-the-33rd-state-to-ratify-convention-108-); [T-PD Bureau report (ratification count)](https://rm.coe.int/t-pd-2026-50rapabr-en/48802c2217)
- [UNICEF Innocenti, Guidance on AI and children 3.0 (December 2025)](https://www.unicef.org/innocenti/reports/policy-guidance-ai-children)
- ICO, Age appropriate design: a code of practice for online services (2020) (link not checked again for this draft).
- [GDPR, Regulation (EU) 2016/679](https://eur-lex.europa.eu/eli/reg/2016/679/oj); [EU AI Act, Regulation (EU) 2024/1689](https://eur-lex.europa.eu/eli/reg/2024/1689/oj)
- [COPPA Rule, 16 CFR Part 312](https://www.ecfr.gov/current/title-16/chapter-I/subchapter-C/part-312); [Jones Day: FTC finalises the COPPA amendments (2025)](https://jonesday.com/en/insights/2025/05/ftc-finalizes-amendments-to-coppa--rule); [FTC COPPA FAQ](https://www.ftc.gov/business-guidance/resources/complying-coppa-frequently-asked-questions)

Store and vendor rules:

- [Apple App Review Guidelines](https://developer.apple.com/app-store/review/guidelines/) (1.3, 4.8, 5.1.1(v), 5.1.2(i), 5.1.4)
- [Google Play Families policy](https://support.google.com/googleplay/android-developer/answer/9893335)
- [OpenAI, Under-18 API guidance](https://developers.openai.com/api/docs/guides/safety-checks/under-18-api-guidance)
- [Anthropic, Responsible use of Anthropic's models: guidelines for organizations serving minors](https://support.claude.com/en/articles/9307344-responsible-use-of-anthropic-s-models-guidelines-for-organizations-serving-minors)
