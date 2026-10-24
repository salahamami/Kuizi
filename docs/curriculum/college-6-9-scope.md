# Scope research: 6e année (primary) and 7e to 9e année de base (collège)

Research note for the re-plan decided by the product owner: Kuizi starts with the **6e année de l'enseignement de base** (السنة السادسة من التعليم الأساسي, last year of primary) and the **7e, 8e and 9e années de base** (السنوات السابعة والثامنة والتاسعة من التعليم الأساسي, the collège or *cycle préparatoire*, المرحلة الإعدادية). The Bac comes later.

**Status:** *to review* (ADR 0005). Facts as of **2026-10-24**, gathered by the Product + Curriculum agent. Nothing here has been checked by a Tunisian teacher yet.

**How to read it.** Each fact carries a source tag such as [S1]; the list is at the end. **Unconfirmed** marks anything that rests on one secondary source, on sources that disagree, or on a text that could not be read. No number in this note was estimated: where a figure was missing, the cell says so.

**Access limits on 2026-10-24.** The official sites `education.gov.tn`, `cnp.com.tn`, `6web.edunet.tn`, `echoexam.edunet.tn` and `neuf.education.tn` answered HTTP 503 to the research tool, and the JORT index `9anoun.tn` timed out on full texts. The concours rules below therefore come from a JORT page copy (2019 arrêté, read in full), from the Ministry's figures as relayed by the press (La Presse, TAP via allAfrica, RTCI and others), and from guidance sites that reproduce official tables. CENAFFIF (vocational trainer training) has no role in these exams and was not used.

## Key findings

1. **Language of instruction.** Every subject of the 6e and of the collège, including mathematics, physical sciences and life and earth sciences, is taught in **Arabic**. The legal basis is article 24 of the Loi d'orientation n° 2002-80 [S5]. French becomes the language of the scientific subjects in the **1ère année secondaire** (first year of lycée) [S45]. French and English are taught as languages. Two initiatives could move this line, but neither has been adopted (section 2.5).
2. **Both concours still exist and are planned for June 2027.** The Ministry published the 2026-2027 calendar on 1 October 2026 [S17, S18]. The neuvième is set for **17, 18 and 19 June 2027** (results Monday 5 July 2027) and the sixième for **21, 22 and 23 June 2027** (results Friday 9 July 2027). No abolition or change to the format has been announced (searched in French and Arabic).
3. **Sixième** (concours d'entrée aux collèges pilotes, مناظرة الدخول إلى المدارس الإعدادية النموذجية): five written papers on the 6e programme, **all with coefficient 1**. They are Arabic (1 h), French (1 h), mathematics (1 h), English (45 min) and *éveil scientifique* (الإيقاظ العلمي, 1 h) [S1, S19]. In 2026: 62,497 registered, 49,661 sat the papers, 17,710 scored at least 10/20 (35.66 %) and 5,317 were admitted to a collège pilote, against 3,850 places set by arrêté [S13, S14, S15].
4. **Neuvième** (diplôme de fin d'études de l'enseignement de base, شهادة ختم التعليم الأساسي العام, which is also the route into the lycées pilotes, المعاهد النموذجية): five papers. They are Arabic composition (coefficient 2), mathematics (2), life and earth sciences (SVT, 2), French (1) and English (1); the total is 8 [S40, S46, S23]. **Physical sciences are not examined.** In 2026: 32,035 registered, 25,301 sat the papers, 16,182 passed (63.96 %) and 6,063 were admitted to lycées pilotes, against 3,750 places [S11, S12, S16].
5. **Results come from the exam alone.** In both concours the ranking uses the concours average only. School marks do not count [S1, arts. 15-16]. Admission needs at least 15/20; remaining places may be filled from 14/20 upward, by merit (amendments of 2021, [S31, S34]).
6. **The smallest subject set that covers both concours** is mathematics, Arabic, French, English and one science (*éveil scientifique* in 6e, SVT in 9e). Mathematics, Arabic and science carry the most weight. **Recommended order:** mathematics, then science, then Arabic, then French, then English (section 6). The evidence supports starting with mathematics.

## 1. Levels and exams at a glance

| Level | French name | Arabic name | National exam at the end | Status |
| --- | --- | --- | --- | --- |
| 6e | 6e année de l'enseignement de base (primary) | السنة السادسة من التعليم الأساسي (المرحلة الابتدائية) | Concours d'entrée aux collèges pilotes, "la sixième" (مناظرة الدخول إلى المدارس الإعدادية النموذجية, «السيزيام») | Optional; only for entry to a collège pilote |
| 7e | 7e année de base | السنة السابعة من التعليم الأساسي | None | Promotion by continuous assessment |
| 8e | 8e année de base | السنة الثامنة من التعليم الأساسي | None | Promotion by continuous assessment |
| 9e | 9e année de base (general) | السنة التاسعة من التعليم الأساسي العام | Diplôme de fin d'études de l'enseignement de base (DFEEB), "la neuvième" (شهادة ختم التعليم الأساسي العام, «النوفيام») | Optional; the route into the lycées pilotes |
| 9e technique | 9e année de base technique | التاسعة أساسي تقني | DFEEB technique (شهادة ختم التعليم الأساسي التقني) | Small track: 5,381 pupils in 9e technique in 2025-2026 [S10] |

All pupils in scope are minors. The sixième is open to pupils who have not repeated a year in primary and are **not over 13 on 15 September** of the year of the concours [S1, art. 3]. Lycées pilotes take pupils **not over 16 on 15 September** of the school year after the DFEEB [S1, p. 2460, art. 3 of the régime arrêté].

## 2. Subjects, weekly hours and language of instruction

### 2.1 Language of instruction

| Stage | Mathematics and sciences | Other subjects | French, English | Evidence |
| --- | --- | --- | --- | --- |
| Primary, 1re to 6e | Arabic (mathematics, *éveil scientifique*, technology education) | Arabic | Taught as languages | Law 2002-80, art. 24 [S5]; CNP 6e textbooks have Arabic titles [S41] |
| Collège, 7e to 9e | **Arabic** (mathematics, sciences physiques, SVT, technology education) | Arabic | Taught as languages | Law 2002-80, art. 24 [S5]; CNP 7e to 9e science textbooks have Arabic titles [S41] |
| Lycée, from the 1ère année secondaire | **French** for the scientific subjects (mathematics, physics, SVT) [S45]; technical, computing and economics subjects are reported in French too (**unconfirmed**) | Arabic | Taught as languages | Leaders, 2023 [S45]; not written in the 2002 law |

- **Law.** Article 24 of the Loi d'orientation n° 2002-80 of 23 July 2002 reads: "Sont enseignées en langue arabe, dans les deux cycles d'enseignement de base, toutes les disciplines ... sociales, scientifiques et techniques" [S5]. The two cycles are the six years of primary and the three years of collège. The copy reproduced by Université Laval labels the law "2002-30"; ILO NATLEX gives n° 2002-80 [S5].
- **The switch.** "Officiellement, l'arabe littéral moderne est la langue choisie pour véhiculer ce savoir jusqu'à la fin de l'école de base"; French then replaces Arabic for the sciences in the first year of secondary [S45].
- **Unconfirmed: collèges pilotes.** One unsourced Arabic Wikipedia table claims that collèges pilotes teach physics in French and computing in English [S51]. No official source was found. To check with a teacher.
- **Unconfirmed: computing (الإعلامية) in collège.** The language of this subject was not found.
- **Unconfirmed: maths notation.** It is likely, but not confirmed, that Arabic-medium maths textbooks write variables and point names in Latin letters, with formulas laid out left to right inside right-to-left text. This matters for rendering items (section 6.4). To check against the CNP textbooks with a maths teacher.
- **Unconfirmed: when French and English start.** In March 2019 the minister announced French from the 2nd year of primary and English from the 4th year, starting the next school year [S47]. Other sources still say the 3rd year for both. Which rule applies now is unconfirmed. Either way, English is in the 6e programme: there is a CNP 6e English textbook [S41] and an English paper in the sixième.

### 2.2 6e année (primary)

**Subjects**, grouped as the school report groups them (domains) [S43]:

| Domain (مجال) | Subjects |
| --- | --- |
| Arabic (مجال اللغة العربية) | Oral communication (تواصل شفوي), grammar (قواعد اللغة), reading (القراءة), written production (الإنتاج الكتابي) |
| Sciences (مجال العلوم) | Mathematics (الرياضيات), *éveil scientifique* (الإيقاظ العلمي), technology education (التربية التكنولوجية) |
| Foreign languages (اللغات الأجنبية) | French (expression orale, production écrite, lecture), English |
| Upbringing (مجال التنشئة) | Islamic education, music, visual arts, history, geography, civic education, physical education |

**Weekly hours: unconfirmed.** The official source is annex 1 of décret gouvernemental n° 2019-1085 of 19 November 2019 [S3], amended by décret n° 2021-143 of 1 March 2021, which replaces tables 5 and 6 of that annex [S4]. Neither full text could be read. One teacher blog without a legal citation gives a weekly plan for the 5e and 6e years [S44]:

| Subject | Weekly time reported [S44], **unconfirmed** |
| --- | --- |
| Mathematics | 5 sessions of 60 min |
| *Éveil scientifique* | 1 session of 60 min |
| Technology education | 1 session of 60 min |
| Arabic (oral, recitation, reading, grammar, writing) | about 5 h 10 min in total |
| History, geography, civic education | 40 min each |
| French, English | Not given |

### 2.3 7e, 8e and 9e année de base (general collège)

The 7e, 8e and 9e share the same subjects, weekly hours and school-report coefficients [S40]. The source cites décret gouvernemental n° 2019-1085 [S3] and the circular of 5 October 2018 on continuous assessment. The table comes from a guidance site; the decree itself could not be read, so the hours are **unconfirmed against the JORT** but consistent across the three year pages.

| Subject (FR) | Subject (AR) | Language of instruction | Hours per week | School-report coefficient |
| --- | --- | --- | --- | --- |
| Arabic (composition, text study) | العربية | Arabic | 5 | 4 |
| French | الفرنسية | French | 4.5 | 4 |
| Mathematics | الرياضيات | Arabic | 4 | 3 |
| English | الأنقليزية | English | 3 | 1.5 |
| History | التاريخ | Arabic | 1 | 1 |
| Geography | الجغرافيا | Arabic | 1 | 1 |
| Islamic education | التربية الإسلامية | Arabic | 1.5 | 1 |
| Civic education | التربية المدنية | Arabic | 1.5 | 1 |
| Physical sciences | العلوم الفيزيائية | Arabic | 1.5 | 1 |
| Life and earth sciences (SVT) | علوم الحياة والأرض | Arabic | 1.5 | 1 |
| Computing | الإعلامية | **Unconfirmed** | 1 | 1 |
| Technology education | التربية التكنولوجية | Arabic | 1.5 | 1 |
| Music | التربية الموسيقية | Arabic | 1 | 1 |
| Visual arts | التربية التشكيلية | Arabic | 1 | 1 |
| Drama (if a teacher is available) | التربية المسرحية | Arabic | 1 | 1 |
| Physical education | التربية البدنية | n/a | 3 | 1 |
| **Total** | | | **33** | **24.5** |

The language column applies article 24 of the 2002 law [S5]. A term average combines control tests, an oral mark (in languages and humanities), practical work (in SVT and computing) and a term test with weight 2 [S40]. Collèges pilotes follow their own *régime d'études* (arrêté of 29 July 2019 [S2]); any extra hours or different languages there are **unconfirmed**.

### 2.4 CNP textbooks (Centre National Pédagogique, المركز الوطني البيداغوجي)

The table is the official CNP list for **2021-2022**, as reproduced by madrassatii.com [S41]; the CNP site itself was unreachable. In August 2026 the CNP's delegated administrator, Karim Daoud, said that no textbook title and no price had changed for the new school year [S42]. Whether every 2021-2022 title is still current, and the exact codes, is **unconfirmed** until the current CNP list is read. Titles are given as printed, including spelling errors in the source.

| Year | Subject | Title (code) |
| --- | --- | --- |
| 6e | Arabic | عالم القراءة – كتاب النصوص (101611); عالم الكتابة – كتاب التمارين (101612) |
| 6e | Mathematics | الرياضيات (102609); كراس الرياضيات (102610) |
| 6e | *Éveil scientifique* | الإيقاظ العلمي (103604) |
| 6e | History and geography | التاريخ والجغرافيا (111612) |
| 6e | French | Un pas de plus vers le collège – Manuel de lecture (121614); Cahier d'activités (121615) |
| 6e | English | Prime English (141604) |
| 7e | Arabic | الأنيس – كتاب النصوص (101708); النحو العربي – كتاب اللغة (101710) |
| 7e | Mathematics | كتاب الرياضيات (102707) |
| 7e | Physical sciences | كتاب العلوم الفيزيائية (103702) |
| 7e | SVT | كتاب علوم الحياة والأرض (105704) |
| 7e | Social studies; Islamic education | كتاب المواد الاجتماعية (111707); كتاب التربية الإسلامية (111706) |
| 7e | Technology education | كتاب الدروس (128701); كراس الأنشطة (128702) |
| 7e | French | Je communique en français (121707) |
| 7e | English | Let's Learn English – Student's Book (141705); Activity Book (141706) |
| 8e | Arabic | نزهة القراءة – كتاب النصوص (101806); النحو العربي – كتاب اللغة (101808) |
| 8e | Mathematics | كتاب الرياضيات (102805) |
| 8e | Physical sciences | كتاب العلوم الفيزيائية (103802) |
| 8e | SVT | كتاب علوم الحياة والأرض (105804) |
| 8e | Islamic education; social studies | كتاب التربية الإسلامية (111807); كتاب المواد الاجتماعية (111809) |
| 8e | Technology education | كتاب الدروس (128801); كراس الأنشطة (128802) |
| 8e | French | Lire et écrire en français (121804) |
| 8e | English | Let's descover more english – Student's book (141806); Activity book (141807) |
| 9e | Arabic | أنوار – كتاب النصوص (101909); النحو العربي – كتاب اللغة (101908) |
| 9e | Mathematics | كتاب الرياضيات (102905) |
| 9e | Physical sciences | كتاب العلوم الفيزيائية (103902) |
| 9e | SVT | كتاب علوم الحياة والأرض (105905) |
| 9e | Islamic education; social studies | التربية الإسلامية (111909); كتاب المواد الاجتماعية (111911) |
| 9e | Technology education | كتاب الدروس (128901); كراس الأنشطة (128902) |
| 9e | French | Pratique du français (121905) |
| 9e | English | Proceed wiht English – Student's book (141906); Activity book (141907) |

Every maths and science textbook from 6e to 9e has an Arabic title, which fits article 24 of the 2002 law. The 2021-2022 list as reproduced shows no separate 6e textbook for Islamic or civic education, and none for computing in 7e to 9e; this is **unconfirmed**. **Rights:** CNP textbooks are Ministry copyright. Kuizi must not copy them beyond what the rights allow (see the agent brief); citing chapter titles to place a concept in the programme is a separate question for the product owner.

**Official programmes (البرامج الرسمية).** The Ministry's programmes page could not be read (HTTP 503). Concept-level programme citations (subject, year, chapter), which T032 requires, need these PDFs. Until they are read, the CNP textbook chapters stand in for them.

### 2.5 Changes under discussion that could move the language line

- **2026-2030 reform.** In a written answer to parliament (reported 19 July 2026), the Ministry listed "la révision de la place des langues dans le système éducatif", seeking "un équilibre entre la consolidation de la langue arabe et l'ouverture sur les langues étrangères". It also listed revised school programmes and reorganised school time [S49]. No date or detail was given.
- **Conseil supérieur de l'éducation et de l'enseignement.** Its members were appointed by ordonnance n° 203 of 12 August 2026, and it held its first session on 17 August 2026 [S50]. No position on languages, exams or pilot schools has been reported.
- **Organic bill n° 117 of 2025** on strengthening the use of English [S52]. According to La Presse, it would make English the main language of instruction from the 2nd year of basic education and the language of the scientific and technological subjects from the collège onward, without dropping French [S48]. The parliamentary education committee held hearings on 16 April 2026. No later stage was found, so its status after April 2026 is **unconfirmed**.

None of these had changed the rules as of 2026-10-24. Kuizi's item model should still not hard-code "collège science means Arabic" (section 6.4).

## 3. Concours d'entrée aux collèges pilotes ("la sixième", «السيزيام»)

### 3.1 Status

- **Held in 2026:** written papers on 22, 23 and 24 June 2026 [S10, S19]. Results were announced on 6 July 2026 [S13], earlier than the 10 July first scheduled [S10].
- **Planned for 2027:** 21, 22 and 23 June 2027, with results on Friday 9 July 2027 (Ministry calendar of 1 October 2026) [S17, S18].
- **Reform:** none announced. Searches in French and Arabic found no abolition or format change. The Le Temps analysis of the 2026 results calls for revised teaching methods, not a new exam [S32].

### 3.2 Rules (arrêté of 29 July 2019, JORT n° 63 of 6 August 2019, pp. 2458-2460 [S1])

- One session at the end of each school year (art. 2).
- **Eligibility:** no repeated year in primary, and not over 13 on 15 September of the year of the concours (art. 3).
- **Registration:** online and individual, with a fee set by a joint arrêté of the finance and education ministers (amount **unconfirmed**). Parents then pick one collège pilote from the regional table (art. 4). The 2019 table lists 26 collèges pilotes, one or more per regional education commissariat (*commissariat régional de l'éducation*); the press counted **27** in 2021 [S30]. The current number is **unconfirmed**.
- **Papers** are set on the 6e programme (art. 7):

| Paper | Arabic name | Duration | Coefficient | 2026 slot [S19] |
| --- | --- | --- | --- | --- |
| Arabic | عربية | 1 h | 1 | Mon 22 June, 08:00-09:00 |
| English | انقليزية | 45 min | 1 | Mon 22 June, 09:30-10:15 |
| French | فرنسية | 1 h | 1 | Tue 23 June, 08:00-09:00 |
| *Éveil scientifique* (science awareness) | إيقاظ علمي | 1 h | 1 | Tue 23 June, 09:30-10:30 |
| Mathematics | رياضيات | 1 h | 1 | Wed 24 June, 08:00-09:00 |

The 2026 timetable matches the 2019 arrêté exactly, so the structure is current. The 2026 papers were published as `Epreuve_arabe_6eme_2026.pdf`, `Epreuve_anglais_…`, `Epreuve_Francais_…`, `Epreuve_eveil_scientifique_…` and `Epreuve_math_6eme_2026.pdf` [S22].

- **What each paper contains: unconfirmed.** A 2016 teacher blog based on a Ministry document describes each paper [S53]:
  - Arabic: a text of 10 to 15 lines, six analysis questions, three syntax and conjugation questions, and a short narrative text of 10 to 15 lines to write.
  - French: a short author's text of about 20 lines, with comprehension, syntax and conjugation questions and a writing task.
  - English: comprehension, language and written expression.
  - Mathematics: three problems covering the programme.
  - *Éveil scientifique*: three physics questions and three biology questions.

  This description predates the 2019 arrêté and must be checked against the 2026 papers.
- **How the result is computed.** It is the concours average only. With five coefficients of 1, it is the plain mean of the five papers. Candidates are ranked by merit for the collège they chose, within its capacity (art. 15). Absence from a paper scores 0 (art. 12). Marks cannot be appealed (art. 11). **School marks do not count.**
- **Admission threshold.** In 2019 it was at least 15/20 (art. 16). The arrêté of 28 April 2021 (JORT of 4 May 2021) replaced art. 16. Candidates with at least 15/20 are admitted, and remaining places may be filled with candidates of at least 14/20, by merit [S31, S30].
- **Accommodations in 2026:** enlarged print for 14 candidates and one third extra time per paper for 67 [S10, S33].

### 3.3 Numbers

| Session | Registered | Sat the papers | At least 10/20 (rate among those present) | Admitted to collèges pilotes | Places | Sources |
| --- | --- | --- | --- | --- | --- | --- |
| 2021 | 53,875 candidates | Not given | Not given | Not given | 3,525 in 27 collèges [S30]; 3,550 for 2021-2022 [S31] (**sources disagree**) | S30, S31 |
| 2024 | Not given | 59,072 | 23,405 (39.67 %); 4,339 at 15/20 or more | 3,680 | 3,850 | S26, S28 |
| 2025 | 64,079 | 51,584 | 17,703 (34.32 %) | 2,683 | 3,850 (arrêté, JORT of 12 May 2025) | S25, S26 |
| 2026 | 62,497 (62,450 before the papers, 29 % of all 6e pupils, 1,608 fewer than in 2025) | 49,661 | 17,710 (35.66 %) | 5,317 | 3,850 (arrêté, JORT of 19 May 2026) | S10, S13, S14, S15 |

- **2026 is above capacity.** RTCI reports that the 3,850 places "a été finalement dépassé pour répondre aux résultats des candidats" [S14]. The rule or decision behind this is **unconfirmed**.
- **2026 capacity by school:** 250 places in Sousse, 225 in Sfax 1, 200 in each of Berges du Lac, Mégrine, Kairouan and Monastir, and 50 to 125 in the interior and the south [S15].
- **Pass rate history** (at least 10/20, which is not the same as admission), as reported: 42.35 % in 2017, 50.35 % in 2019, 39.04 % in 2022 [S26]; about 42 % in 2017 and 2018, 45.44 % in 2020, 36.15 % in 2023 [S32].
- **Where the gaps are.** A teacher quoted on the 2026 results said the gaps are "tout particulièrement marqués en français et en mathématiques"; private schools score above public ones [S32].

### 3.4 Past papers

- **Official:** the Ministry portal for this concours is `6web.edunet.tn` (unreachable on 2026-10-24).
- **Secondary:** Orientini publishes the 2026 papers as PDF [S22], and teacher sites publish older papers with corrections. The rights and the accuracy of these copies are **unconfirmed**. Ask the product owner before reusing any of them.

## 4. Lycées pilotes through the neuvième («النوفيام»)

### 4.1 Status

- **There is no separate entrance exam.** Lycées pilotes take the pupils who pass the **DFEEB with distinction** and meet the age and record conditions [S1, p. 2460, art. 3]. The DFEEB is **optional**: promotion to the 1ère année secondaire depends on the 9e annual average. A pupil who fails the annual average can still move up by passing the DFEEB [S40].
- **Held in 2026:** written papers on 18, 19 and 20 June 2026 [S10, S20]. Results were announced on 2 July 2026 [S11], earlier than the 6 July first scheduled [S10].
- **Planned for 2027:** 17, 18 and 19 June 2027 for the general and technical DFEEB, with results on Monday 5 July 2027 [S18].
- **Reform:** none announced.

### 4.2 Rules

- **Legal basis.** Décret gouvernemental n° 2019-656 of 29 July 2019 sets the admission criteria for lycées pilotes [S2]. It was amended by décret gouvernemental n° 2021-342 of 7 May 2021 (JORT of 21 May 2021) [S34]. The DFEEB exam itself is governed by an arrêté of 20 May 2009, amended in 2013, which the capacity arrêtés cite [S6, S7]. **None of these texts was read in full.**
- **Eligibility for a lycée pilote:** not over 16 on 15 September of the school year after the DFEEB [S1, p. 2460], and no repeated year in primary or collège [S40].
- **Papers.** Two secondary sources agree on the coefficients, and the 2026 papers match the list. Durations differ for SVT.

| Paper | Arabic name | Duration | Coefficient | 2026 day [S20] |
| --- | --- | --- | --- | --- |
| Arabic composition | الإنشاء العربي | 2 h | 2 | Thu 18 June |
| English (text study) | الأنقليزية | 1 h | 1 | Thu 18 June |
| French (text study) | الفرنسية | 2 h | 1 | Fri 19 June |
| Life and earth sciences (SVT) | علوم الحياة والأرض | 1 h [S40] or 2 h [S46]: **unconfirmed** | 2 | Fri 19 June |
| Mathematics | الرياضيات | 2 h | 2 | Sat 20 June |
| **Total** | | | **8** | |

Sources: coefficients and durations from tawjih.tn [S40] and a 2016 teacher blog [S46]; the 2026 papers (Arabic, English, French, SVT, maths) were published as `Epreuve_*_9eme_generale_2026.pdf` [S23]. Start times are **unconfirmed** (the calendar is an image). La Presse lists "mathématiques et arabe" for Saturday [S21], while Orientini lists only mathematics [S20]. The coefficients are **unconfirmed against the JORT text**.

- **Physical sciences, history and geography, Islamic and civic education, technology and computing are not examined.**
- **How the result is computed.** It is the coefficient-weighted average of the five papers. A pass is 10/20. Lycée pilote admission needs at least 15/20, with remaining places filled from 14/20 upward by merit [S34, S26]. The press reports that the Ministry has sometimes admitted pupils below 15/20 "sous la pression de certains parents" [S26] (**unconfirmed**). **School marks do not count** in the exam average.
- **Accommodations in 2026:** enlarged print for 14 candidates, Braille for 1 and one third extra time for 67 [S10].

### 4.3 Numbers (general track)

| Session | Registered | Sat the papers | Passed (rate among those present) | Admitted to lycées pilotes | Places | Sources |
| --- | --- | --- | --- | --- | --- | --- |
| 2024 | Not given | 26,061 | 16,936 (64.99 %) | 3,515 | 3,750 (arrêté of 22 May 2024) | S29, S7 |
| 2025 | 33,183 | 25,827 | 16,290 (63.07 %) | 4,287 | 3,750 (arrêté of 12 May 2025) | S26, S27, S6 |
| 2026 | 32,035 (32,004 before the papers, 18 % of 175,024 9e general pupils, 1,163 fewer than in 2025) | 25,301 | 16,182 (63.96 %) | 6,063 | 3,750 (JORT of 19 May 2026) | S10, S11, S12, S16 |

- **Technical track:** in 2025, 308 registered, 263 sat the papers and 148 passed (56.27 %) [S27]; in 2026, 203 registered, 164 sat the papers and 112 passed (68.29 %) [S11].
- **Pass rate history** (general), as reported: 51.26 % in 2017, 45.94 % in 2018, 66.98 % in 2019, 60.24 % in 2020, 62.09 % in 2021, 53.94 % in 2022, 60.56 % in 2023 [S26].
- **2026 places by school:** Tunis (Bourguiba) 300, Sousse 275, Sfax 1 250, and Kasserine and Gafsa 150 each [S16].
- Admissions went over the 3,750 places in 2025 and 2026; the reason is **unconfirmed**.

### 4.4 Past papers

- **Official:** the Ministry portals are `echoexam.edunet.tn` and `neuf.education.tn` (unreachable on 2026-10-24).
- **Secondary:** Orientini publishes the 2026 papers [S23]. The same caution on rights applies as for the sixième.

## 5. Other national evaluations

- **DFEEB (general and technical):** it exists in 2026 and is scheduled for June 2027 (section 4). It is optional and is the only national exam at the end of the collège.
- **7e and 8e:** there is no national exam. Promotion depends on the annual average of continuous assessment, with the coefficients in section 2.3 [S40].
- **6e:** the sixième concours is the only national exam at the end of primary, and it is optional. In 2026, 29 % of 6e pupils registered [S10]. No other end-of-primary national exam was found.
- **National or international learning surveys** (for example a national assessment of learning outcomes, or TIMSS) do not decide anything for a pupil. No recent cycle for these years was confirmed (**unconfirmed**).

## 6. What this means for Kuizi

### 6.1 The smallest subject set that covers both concours

Five subjects: **mathematics, Arabic, French, English and one science** (*éveil scientifique* in 6e, SVT in 7e to 9e). Every concours paper falls in these five. The sixième covers the 6e programme only [S1, art. 7]. Whether the neuvième examines only the 9e programme or also earlier years is **unconfirmed**.

Subjects that appear in **neither** concours: physical sciences (except as part of 6e *éveil scientifique*), history and geography, Islamic and civic education, technology education, computing and the arts. They still count in the school-report average (coefficient 1 each in collège) and in 7e to 9e promotion.

### 6.2 Weight of each subject

| Subject | Sixième share | Neuvième share | Mean of the two exams | Collège school report (of 24.5) |
| --- | --- | --- | --- | --- |
| Mathematics | 20 % | 25 % | 22.5 % | 12.2 % (3) |
| Arabic | 20 % | 25 % (composition) | 22.5 % | 16.3 % (4) |
| Science (*éveil scientifique* in 6e, SVT in 9e) | 20 % | 25 % | 22.5 % | 4.1 % (SVT 1) and 4.1 % (physics 1) |
| French | 20 % | 12.5 % | 16.25 % | 16.3 % (4) |
| English | 20 % | 12.5 % | 16.25 % | 6.1 % (1.5) |

Shares are coefficient over total coefficient (sixième 5, neuvième 8, school report 24.5). The mean column weights the two exams equally. That is a simplification: the sixième had about twice as many candidates in 2026 (62,450 against 32,004 [S10]).

### 6.3 Recommended order

1. **Mathematics, 6e then 9e, with 7e and 8e filled in as the prerequisites 9e needs, then complete.** The evidence supports starting here:
   - Mathematics is examined in both concours and carries the top weight in the neuvième (tied with Arabic and SVT).
   - The 6e maths paper and the larger candidate pool (about 62,000) make the sixième the first deadline: 21 to 23 June 2027.
   - Maths answers are numbers, expressions and choices, which suit auto-graded items and knowledge tracing better than essays.
   - Maths is strongly cumulative, so the concept graph and prerequisite routing (T052, T053) show their value. A 9e pupil can be sent back to a 6e or 7e gap.
   - Press reports on the 2026 results single out maths (and French) as the weak areas [S32].
2. **Science: *éveil scientifique* in 6e and SVT in 7e to 9e.** It weighs 20 % in the sixième and 25 % in the neuvième, it is Arabic-medium, and it suits multiple-choice items with distractor rationales. Physical sciences come later. They are not in the neuvième, so the Bac Physics seed in `curriculum/graph/` (French, 4e année secondaire) is not reusable here.
3. **Arabic.** It carries as much weight as maths, and reading comprehension underpins every Arabic-medium word problem. Most of the 6e Arabic paper (comprehension, syntax, conjugation) can be broken into items, but it also has a short narrative writing task [S53]. The neuvième paper, though, is a two-hour composition (الإنشاء), which needs writing assessment by a teacher or an assisted grader. That is a new capability and possibly a new dependency, so it needs a product owner decision.
4. **French.** It weighs 20 % in the sixième, 12.5 % in the neuvième and 16.3 % of the school report. It is also the language of the sciences from lycée onward. A cheap first step is to give every maths and science concept a French term next to the Arabic one. That prepares the 9e to lycée transition and the later Bac without writing a French course yet.
5. **English.** It weighs 20 % in the sixième and 12.5 % in the neuvième.

**Where the evidence argues otherwise.** The sixième weights its five papers equally, so maths alone covers only a fifth of that score. If the product owner's first goal is the sixième market, a full 6e pack (all five 1-hour papers on the 6e programme) is the alternative to depth in maths from 6e to 9e. A second point: French matters more for school-report averages (coefficient 4) than for either concours. The recommendation above stays with maths first, then science, and treats a full 6e pack as the second option.

### 6.4 Consequences for the content model and the backlog

These are notes for the main session; this research changes no ticket.

- **Arabic-first content.** For 6e to 9e, the authoritative exam language of maths and science items is Arabic (Modern Standard Arabic), the reverse of the Bac assumption. The Definition of Done still asks for French and Arabic on every item; for this scope the French version is a support and bridge layer. The item model (T036) needs a field saying which language is authoritative. Do not tie the language to the subject, because the line may move (section 2.5).
- **Right-to-left maths.** Arabic-medium maths may mix right-to-left text with left-to-right formulas and Latin letters (**unconfirmed**, section 2.1). Item rendering and the design system need a rule for bidirectional maths (WCAG 2.2 AA, screen readers).
- **Subjects and tracks (T033).** New levels are needed: 6e primary and 7e, 8e and 9e de base, general track, with the technical track as a later option. A collège pilote is a school type, not a separate programme (**unconfirmed**, pending the régime d'études arrêté [S2]). Concepts need `exam_weight` values for the sixième and the neuvième (section 6.2).
- **Programme citations (T032 Definition of Done).** The official 6e and 7e to 9e programmes must be obtained. The Ministry site was unreachable; the CNP textbook chapters can stand in until then.
- **Minors.** Pupils are about 11 to 15 years old (inferred from the age caps in section 1). Parental consent (T013) and Law 2004-63 apply to every user. The sixième audience is younger than the Bac audience, and parents are likely the buyers.
- **Accessibility.** Both concours grant enlarged print, Braille and one third extra time [S10]. Kuizi's timed practice should offer an extended-time setting. That is accommodation data, which is sensitive.
- **Timing.** By the sprint convention in `CLAUDE.md`, the June 2027 exams (17 to 23 June) fall in APL Sprint 18 (2027-06-14 to 2027-06-25). The cloud move T240 is planned for Sprint 11 (2027-03-08 to 2027-03-19). Real pupils can therefore only use Kuizi for the last revision months before the exams, unless the plan changes.
- **Rights.** Past papers belong to the Ministry and textbooks to the CNP. Get the product owner's approval before reusing any text, figure or paper (agent brief), and record the source and rights of each.

## 7. Unconfirmed items to resolve (with a Tunisian teacher or the official texts)

1. Exact weekly hours for 6e primary (annex 1 of décret 2019-1085 as amended by décret 2021-143), and the JORT text behind the collège hours.
2. Coefficients and durations of the DFEEB papers from the JORT text (arrêté of 20 May 2009 as amended); the SVT duration (1 h or 2 h).
3. Whether the neuvième examines only the 9e programme or earlier years too.
4. What each sixième paper contains (structure of the 2026 papers).
5. Language of computing in collège; whether collèges pilotes teach any science in French.
6. Maths notation conventions in Arabic-medium textbooks (Latin letters, direction of formulas).
7. Year in which French and English start in primary today.
8. Current number of collèges pilotes and lycées pilotes; why admissions went over capacity in 2026; the 2021 capacity (3,525 or 3,550).
9. The current CNP titles and codes for 2026-2027.
10. Status of organic bill n° 117/2025 after April 2026, and any language decision of the 2026-2030 reform.
11. The sixième registration fee.

## Sources

Accessed 2026-10-24.

**Official and legal texts**

- [S1] JORT n° 63 of 6 August 2019, pp. 2458-2460: arrêté of the Minister of Education of 29 July 2019 on the criteria of the concours d'entrée aux collèges pilotes, and (p. 2460) the start of the arrêté of the same date on the régime d'études of the collèges and lycées pilotes. Copy hosted by tawjih.tn: <https://tawjih.tn/pdf/2019_Arrete_29_7_2019_criteres_concours_6eme.pdf>
- [S2] Arrêté of 29 July 2019 on the régime d'études of the collèges and lycées pilotes, which cites décret gouvernemental n° 2019-656 (JORT index): <https://9anoun.tn/fr/kb/jorts/jort-2019-063-5ba93/arrete-du-ministre-de-l-education-du-29-juillet-2019-fixant-le-regime-d-etudes-aux-colleges-pilotes-et-aux-lycees-pilotes-58>
- [S3] Décret gouvernemental n° 2019-1085 of 19 November 2019 on the hours of study in basic and secondary education (index; full text timed out): <https://9anoun.tn/fr/kb/jorts/jort-2019-095-424da/decret-gouvernemental-ndeg-2019-1085-du-19-novembre-2019-fixant-lhoraire-des-etudes-dans-lenseignement-de-base-et-dans-lenseignement-secondaire-60>
- [S4] Décret gouvernemental n° 2021-143 of 1 March 2021 amending décret 2019-1085 (index): <https://9anoun.tn/fr/kb/jorts/jort-2021-022-ae9df/decret-gouvernemental-ndeg-2021-143-du-1er-mars-2021-modifiant-le-decret-gouvernemental-ndeg-2019-1085-du-19-novembre-2019-fixant-lhoraire-des-etudes-dans-lenseignement-de-base-et--5cae85b018dea9894163eae4e6c6a61b>
- [S5] Loi d'orientation n° 2002-80 of 23 July 2002 on education and school teaching, art. 24. Text reproduced by CEFAN, Université Laval (labelled "2002-30"): <https://www.axl.cefan.ulaval.ca/afrique/tunisie-loi-2002-educ.htm>. ILO NATLEX record: <https://www.ilo.org/dyn/natlex/natlex4.detail?p_lang=fr&p_isn=61806&p_country=TUN&p_count=1034&p_classification=09&p_classcount=83>
- [S6] Arrêté of 12 May 2025 setting the capacity of the lycées pilotes for 2025-2026 (JORT 2025-056, index): <https://9anoun.tn/fr/kb/jorts/jort-2025-056-ad17a/arrete-du-ministre-de-l-education-du-12-mai-2025-fixant-la-capacite-daccueil-des-lycees-pilotes-pour-lannee-scolaire-2025-2026-20>
- [S7] Arrêté of 22 May 2024 setting the capacity of the lycées pilotes for 2024-2025 (JORT 2024-064, index): <https://www.9anoun.tn/fr/kb/jorts/jort-2024-064-1d6ec/arrete-de-la-ministre-de-l-education-du-22-mai-2024-fixant-la-capacite-daccueil-des-lycees-pilotes-pour-lannee-scolaire-2024-2025-47>

**Official sources that could not be read on 2026-10-24 (HTTP 503):** Ministry of Education programmes page <https://education.gov.tn/?p=500&lang=en>; CNP official textbook list <https://www.cnp.com.tn/arabic/annee-actuelle/listeOfficielle.htm>; sixième portal <http://www.6web.edunet.tn/>; exam portal <http://www.echoexam.edunet.tn/>; neuvième portal <https://neuf.education.tn/>.

**Ministry figures and calendars, as reported by the press**

- [S10] La Presse, 2026-06-02, "Baisse du nombre de candidats aux concours de la sixième et de la neuvième": <https://www.lapresse.tn/2026/06/02/baisse-du-nombre-de-candidats-aux-concours-de-la-sixieme-et-de-la-neuvieme/>
- [S11] La Presse, 2026-07-02, "Concours de la neuvième année de base: un taux de réussite de 63.96%": <https://www.lapresse.tn/2026/07/02/concours-de-la-neuvieme-annee-de-base-un-taux-de-reussite-de-63-96/>
- [S12] TAP via allAfrica, 2026-07-02, "Neuvième - Plus de 6 mille candidats affectés aux lycées pilotes": <https://fr.allafrica.com/stories/202607020550.html>
- [S13] La Presse, 2026-07-06, "Sixième 2026 : 5 317 élèves orientés vers les collèges pilotes": <https://www.lapresse.tn/2026/07/06/sixieme-2026-5-317-eleves-orientes-vers-les-colleges-pilotes/>
- [S14] RTCI, 2026-07-06, "Concours des collèges pilotes 2026 : plus de 5 300 élèves admis": <https://www.rtci.tn/article/6a4bee9408d2abfa30623d03/concours-des-coll%C3%A8ges-pilotes-2026--plus-de-5-300-%C3%A9l%C3%A8ves-admis>
- [S15] La Presse, 2026-05-19, "Collèges pilotes : la capacité d'accueil fixée à 3850 places": <https://www.lapresse.tn/2026/05/19/colleges-pilotes-la-capacite-daccueil-fixee-a-3850-places-au-titre-de-lannee-scolaire-2026-2027/>
- [S16] webdo, 2026-05-19, "Lycées pilotes : le ministère de l'Éducation fixe les quotas par région": <https://www.webdo.tn/fr/actualite/national/lycees-pilotes-le-ministere-de-leducation-fixe-les-quotas-par-region/398308/>
- [S17] La Presse, 2026-10-01, "Le ministère de l'Éducation dévoile le calendrier des examens nationaux 2026-2027": <https://www.lapresse.tn/2026/10/01/le-ministere-de-leducation-devoile-le-calendrier-des-examens-nationaux-2026-2027/>
- [S18] L'écho tunisien, 2026-10-02, "Calendrier officiel des épreuves et examens nationaux 2026-2027": <https://lechotunisien.com/tunisie-calendrier-officiel-des-epreuves-et-examens-nationaux-2026-2027/>
- [S19] Orientini, 2025-12-27, "سيزيام 2026 : روزنامة الاختبارات الكتابية" (Ministry timetable reposted): <https://www.orientini.com/FR/Annonces_Orientation_Formation_Emploi/16682/>
- [S20] Orientini, 2025-12-27, "روزنامة الإختبارات الكتابية - امتحان شهادة ختم التعليم الأساسي العام (نوفيام 2026)": <https://www.orientini.com/FR/Annonces_Orientation_Formation_Emploi/16683/>
- [S21] La Presse, 2026-06-17, "Neuvième : le ministère de l'Éducation publie le calendrier des examens": <https://www.lapresse.tn/2026/06/17/neuvieme-le-ministere-de-leducation-publie-le-calendrier-des-examens/>
- [S22] Orientini, 2026-06, the 2026 sixième papers (PDF): <https://orientini.com/AR/Annonces_Orientation_Formation_Emploi/17448/_%D8%B3%D9%8A%D8%B2%D9%8A%D8%A7%D9%85-2026-:-%D9%86%D8%B5%D9%88%D8%B5-%D8%A7%D8%AE%D8%AA%D8%A8%D8%A7%D8%B1%D8%A7%D8%AA-%D9%85%D9%86%D8%A7%D8%B8%D8%B1%D8%A9-%D8%A7%D9%84%D8%AF%D8%AE%D9%88%D9%84-%D8%A5%D9%84%D9%89-%D8%A7%D9%84%D9%85%D8%AF%D8%A7%D8%B1%D8%B3-%D8%A7%D9%84%D8%A5%D8%B9%D8%AF%D8%A7%D8%AF%D9%8A%D8%A9-%D8%A7%D9%84%D9%86%D9%85%D9%88%D8%B0%D8%AC%D9%8A%D8%A9>
- [S23] Orientini, 2026-06-18, the 2026 DFEEB general papers (PDF): <https://www.orientini.com/FR/Annonces_Orientation_Formation_Emploi/17417/>
- [S24] Ultra Tunisia, 2025-12-27, detailed calendar of the 2025-2026 national exams: <https://ultratunisia.ultrasawt.com/%D8%A7%D9%84%D8%B1%D9%88%D8%B2%D9%86%D8%A7%D9%85%D8%A9-%D8%A7%D9%84%D8%AA%D9%81%D8%B5%D9%8A%D9%84%D9%8A%D8%A9-%D9%84%D8%A7%D8%AE%D8%AA%D8%A8%D8%A7%D8%B1%D8%A7%D8%AA-%D8%A7%D9%84%D8%A7%D9%85%D8%AA%D8%AD%D8%A7%D9%86%D8%A7%D8%AA-%D8%A7%D9%84%D9%88%D8%B7%D9%86%D9%8A%D8%A9-%D9%84%D9%84%D8%B3%D9%86%D8%A9-%D8%A7%D9%84%D8%AF%D8%B1%D8%A7%D8%B3%D9%8A%D8%A9-2025-2026/%D8%A7%D9%84%D8%AA%D8%B1%D8%A7-%D8%AA%D9%88%D9%86%D8%B3/%D9%85%D8%AC%D8%AA%D9%85%D8%B9/%D8%A7%D9%94%D8%AE%D8%A8%D8%A7%D8%B1>
- [S25] Tunisie-Tribune, 2025-07-01, "Concours de la 6ème : 2683 élèves affectés aux collèges pilotes": <https://www.tunisie-tribune.com/2025/07/01/concours-de-la-6eme-2683-eleves-affectes-aux-colleges-pilotes-pour-lannee-scolaire-2025-2026/>
- [S26] La Presse, 2025-07-05, "Examens : coup de projecteur sur la sixième et la neuvième": <https://www.lapresse.tn/2025/07/05/examens-coup-de-projecteur-sur-la-sixieme-et-la-neuvieme/>
- [S27] Univers News, 2025-07, "Résultat de la neuvième 2025 : 4287 orientés vers les lycées pilotes": <https://universnews.tn/resultat-de-la-neuvieme-2025-4287-orientes-vers-les-lycees-pilotes/>
- [S28] webdo, 2024-07-05, "39,67% de réussite au concours de la sixième": <https://www.webdo.tn/fr/actualite/national/tunisie-39-67-de-reussite-au-concours-de-la-sixieme/215094/>
- [S29] African Manager, 2024-07-09, "Neuvième : 3 515 élèves affectés aux lycées pilotes": <https://africanmanager.com/?p=503816>
- [S30] Directinfo, 2021-06-28, "Démarrage des épreuves du concours d'accès aux collèges pilotes": <https://directinfo.webmanagercenter.com/2021/06/28/tunisie-demarrage-des-epreuves-du-concours-dacces-aux-colleges-pilotes/>
- [S31] Orientini, 2021-05-04, "تنقيح معايير القبول بالمدارس الإعدادية النموذجية" (new art. 16, JORT of 4 May 2021): <https://www.orientini.com/AR/Annonces_Orientation_Formation_Emploi/10244/>
- [S32] Le Temps, 2026-07-08, "Concours d'accès aux collèges pilotes : légère amélioration du taux de réussite": <https://letemps.news/2026/07/08/concours-dacces-aux-colleges-pilotes-legere-amelioration-du-taux-de-reussite/>
- [S33] Tekiano, 2026-06-22, "Concours 6ème 2026 : 62 450 élèves pour 3 850 sièges": <https://www.tekiano.com/2026/06/22/concours-6eme-2026-62-450-eleves-pour-3-850-sieges-dans-les-colleges-pilotes-tunisiens/>
- [S34] Ultra Tunisia, 2021-05, "مقاييس جديدة للالتحاق بالمعاهد النموذجية" (décret 2021-342). The page now returns 404; its content was read in the search index only: <https://ultratunisia.ultrasawt.com/مقاييس-جديدة-للالتحاق-بالمعاهد-النموذجية/الترا-تونس/مجتمع/أخبار>

**Reference and secondary sources**

- [S40] tawjih.tn, collège study system tables (citing décret 2019-1085) and the neuvième page: <https://tawjih.tn/college/7b/2/>, <https://tawjih.tn/college/8b/1/>, <https://tawjih.tn/college/9b/1/>, <https://tawjih.tn/college/9b/3/>
- [S41] madrassatii.com, CNP official textbook list for 2021-2022: <https://madrassatii.com/%D8%A7%D9%84%D9%82%D8%A7%D8%A6%D9%85%D8%A9-%D8%A7%D9%84%D8%B1%D8%B3%D9%85%D9%8A%D8%A9-%D9%84%D9%84%D9%83%D8%AA%D8%A8-%D8%A7%D9%84%D9%85%D8%AF%D8%B1%D8%B3%D9%8A%D8%A9-%D9%84%D8%B3%D9%86%D8%A9-2021-2022/>
- [S42] Hakaek Online, 2026-08-31, CNP: no change in textbook titles or prices: <https://hakaekonline.com/%D9%84%D9%84%D9%85%D8%B1%D9%83%D8%B2-%D8%A7%D9%84%D9%88%D8%B7%D9%86%D9%8A-%D8%A7%D9%84%D8%A8%D9%8A%D8%AF%D8%A7%D8%BA%D9%88%D8%AC%D9%8A-%D9%84%D8%A7-%D8%AA%D8%BA%D9%8A%D9%8A%D8%B1-%D9%81%D9%8A-%D8%A3%D8%B3%D8%B9%D8%A7%D8%B1-%D9%88%D8%B9%D9%86%D8%A7%D9%88%D9%8A%D9%86-%D8%A7%D9%84%D9%83%D8%AA%D8%A8-%D8%A7%D9%84%D9%85%D8%AF%D8%B1%D8%B3%D9%8A%D8%A9-%D9%88%D8%A7%D8%B3%D8%AA%D9%83%D9%85%D8%A7%D9%84-%D8%A7%D9%84%D8%AA%D9%88%D8%B2%D9%8A%D8%B9-%D8%A7%D9%84%D8%A3%D8%B3%D8%A8%D9%88%D8%B9-%D8%A7%D9%84%D9%85%D9%82%D8%A8%D9%84/>
- [S43] Devoir.TN, 6e primary average calculator (domains and subjects): <https://www.devoir.tn/news/moyenne/primaire-6eme>
- [S44] Bibliothèque éducative (teacher blog), 2025-09, weekly distribution of subjects in primary: <https://bibliotheque-educative.blogspot.com/2025/09/distribution-study-materials-over-weekly-classes.html>
- [S45] Habib Batis, "La transition linguistique et l'enseignement en Tunisie: Apprentissage des sciences", Leaders, 2023-10-18: <https://www.leaders.com.tn/article/35262-la-transition-linguistique-et-l-enseignement-apprentissage-des-sciences>
- [S46] Blog pédagogique (A. Bouhouch), 2016-06, "Le diplôme de fin d'étude de l'enseignement de base général": <http://bouhouchakrout.blogspot.com/2016/06/le-diplome-de-fin-detude-de.html>
- [S47] Orientini, 2019-03-15, Ministry announcement on French from the 2nd year and English from the 4th year: <https://orientini.com/AR/Annonces_Orientation_Formation_Emploi/5571/_%D9%88%D8%B2%D8%A7%D8%B1%D8%A9-%D8%A7%D9%84%D8%AA%D8%B1%D8%A8%D9%8A%D8%A9-:-%D8%A7%D9%84%D8%A5%D8%B9%D9%84%D8%A7%D9%86-%D8%B9%D9%86-%D8%A5%D8%AF%D8%B1%D8%A7%D8%AC--%D8%A7%D9%84%D9%81%D8%B1%D9%86%D8%B3%D9%8A%D8%A9-%D9%81%D9%8A-%D8%A7%D9%84%D8%B3%D9%86%D8%A9-%D8%A7%D9%84%D8%AB%D8%A7%D9%86%D9%8A%D8%A9-%D9%88%D8%A7%D9%84%D8%A5%D9%86%D9%83%D9%84%D9%8A%D8%B2%D9%8A%D8%A9-%D9%81%D9%8A-%D8%A7%D9%84%D8%B3%D9%86%D8%A9-%D8%A7%D9%84%D8%B1%D8%A7%D8%A8%D8%B9%D8%A9>
- [S48] La Presse, 2026-04-16, "Enseignement de l'anglais à partir de la deuxième année primaire : un projet de loi proposé à l'ARP": <https://www.lapresse.tn/2026/04/16/enseignement-de-langlais-a-partir-de-la-deuxieme-annee-primaire-un-projet-de-loi-propose-a-larp/>
- [S49] La Presse, 2026-07-19, "Le ministère de l'Éducation injecte 717 millions de dinars pour lancer une grande réforme scolaire": <https://www.lapresse.tn/2026/07/19/le-ministere-de-leducation-injecte-717-millions-de-dinars-pour-lancer-une-grande-reforme-scolaire/>
- [S50] webdo, 2026-08, "Réforme de l'éducation : le Conseil supérieur, dès lundi, dans sa phase opérationnelle": <https://www.webdo.tn/fr/actualite/national/reforme-de-leducation-le-conseil-superieur-des-lundi-dans-sa-phase-operationnelle/402626/>
- [S51] Arabic Wikipedia, "التعليم في تونس" (hours table without sources; used only to flag a claim): <https://ar.wikipedia.org/wiki/%D8%A7%D9%84%D8%AA%D8%B9%D9%84%D9%8A%D9%85_%D9%81%D9%8A_%D8%AA%D9%88%D9%86%D8%B3>
- [S52] Tunisie Numérique, 2026-04-16, "Au Parlement, l'encadrement du privé et le renforcement de l'anglais à l'examen" (bill n° 117 of 2025): <https://www.tunisienumerique.com/au-parlement-lencadrement-du-prive-et-le-renforcement-de-langlais-a-lexamen/>
